#!/usr/bin/env python3
"""Read-only GitHub-side evaluation of PythonAnywhere's published health evidence.

This is independent of the PythonAnywhere runtime and requires no credentials.
Exit 1 on missing, stale or degraded agent evidence; never print diagnostics
that could contain private tokens, email subjects or other personal details.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

AGENTS = tuple(f"ACS-0{i}" for i in range(1, 6))
MAX_SNAPSHOT_AGE_HOURS = 36.0
MAX_AGENT_AGE_HOURS = 36.0
MAX_FUTURE_SECONDS = 300


def parse_timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("missing timestamp")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return stamp.astimezone(timezone.utc)


def evaluate(data: dict, now: datetime | None = None) -> list[str]:
    now = datetime.now(timezone.utc) if now is None else now
    problems: list[str] = []
    if not isinstance(data, dict) or data.get("source") != "pythonanywhere":
        return ["snapshot source is missing or invalid"]
    try:
        age = (now - parse_timestamp(data.get("generated_at_utc"))).total_seconds()
        if age < -MAX_FUTURE_SECONDS or age > MAX_SNAPSHOT_AGE_HOURS * 3600:
            problems.append("snapshot is stale or future-dated")
    except (ValueError, OverflowError, TypeError):
        problems.append("snapshot timestamp is invalid")

    agents = data.get("agents")
    if not isinstance(agents, dict):
        return problems + ["agent evidence is missing"]
    for name in AGENTS:
        agent = agents.get(name)
        if not isinstance(agent, dict):
            problems.append(f"{name}: evidence missing")
            continue
        if agent.get("verified") is not True:
            problems.append(f"{name}: evidence not verified")
        if agent.get("health_status") not in ("ok", "healthy"):
            problems.append(f"{name}: unhealthy state")
        if agent.get("status") not in ("current", "healthy"):
            problems.append(f"{name}: not current")
        try:
            run_age = (now - parse_timestamp(agent.get("last_execution_utc"))).total_seconds()
            if run_age < -MAX_FUTURE_SECONDS or run_age > MAX_AGENT_AGE_HOURS * 3600:
                problems.append(f"{name}: execution evidence is stale or future-dated")
        except (ValueError, TypeError, OverflowError):
            problems.append(f"{name}: execution timestamp invalid")
    schedule = data.get("pythonanywhere_schedule")
    if isinstance(schedule, dict) and schedule.get("available") is True:
        for key in ("acs01_task", "health_task"):
            task = schedule.get(key)
            if not isinstance(task, dict) or task.get("enabled") is not True:
                problems.append(f"{key}: scheduled task not enabled")
    return problems


def main() -> int:
    path = Path("logs/system/pythonanywhere_health.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        problems = evaluate(data)
    except (OSError, ValueError, UnicodeError) as exc:
        # Exception type only: do not echo source data in CI output.
        problems = [f"snapshot unreadable: {type(exc).__name__}"]

    for problem in problems:
        print(f"::error title=AI Consensus health check::{problem}")
    if problems:
        print(f"FAIL: {len(problems)} health checks failed; inspect PythonAnywhere securely.")
        return 1
    print("PASS: published PythonAnywhere evidence is fresh and all ACS-01..05 healthy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
