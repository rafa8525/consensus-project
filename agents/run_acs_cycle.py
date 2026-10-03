#!/usr/bin/env python3
"""Authoritative ACS-02..ACS-05 execution harness.

Health states:
  healthy           = work completed and verified
  warning           = work completed but a non-critical condition needs attention
  critical          = verified serious health problem
  execution_failure = requested work could not be completed

ACS-02 performs real absorption before publishing/verifying its success marker.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path.home() / "consensus-project"
RUNTIME_MEMORY = Path.home() / "memory"
STATE = REPO / "memory" / "agents"
PYTHON = sys.executable

ABSORB_WORKER = REPO / "tools" / "absorb_memory.py"
ABSORB_MARKER_WRITER = REPO / "tools" / "write_absorption_public_marker.py"
ABSORB_MARKER = RUNTIME_MEMORY / "public" / "absorption_last_success.json"
ABSORB_MAX_AGE_HOURS = 36.0

CYCLES = {
    "ACS-03": [
        ("fitness_tracking_verifier", REPO / "tools/fitness_tracking_verifier.py"),
        ("health_master", REPO / "tools/health_master.py"),
        ("backup_fitness", REPO / "tools/backup_fitness.py"),
    ],
    "ACS-04": [
        ("infrastructure_guardian", REPO / "agents/infrastructure_guardian.py"),
    ],
    "ACS-05": [
        ("continuity_guardian", REPO / "agents/continuity_guardian_agent.py"),
    ],
}

SEVERITY = {
    "healthy": 0,
    "warning": 1,
    "critical": 2,
    "execution_failure": 3,
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_utc(value: str) -> datetime:
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def run_process(component: str, path: Path, extra: list[str] | None = None) -> dict:
    cmd = [PYTHON, str(path)]
    if extra:
        cmd.extend(extra)

    try:
        p = subprocess.run(
            cmd,
            cwd=REPO,
            text=True,
            capture_output=True,
            timeout=900,
        )
    except Exception as exc:
        return {
            "component": component,
            "status": "execution_failure",
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
        }

    stdout = p.stdout[-4000:]
    stderr = p.stderr[-4000:]

    if component == "infrastructure_guardian":
        status = {
            0: "healthy",
            1: "warning",
            2: "critical",
            3: "execution_failure",
        }.get(p.returncode, "execution_failure")

    elif component == "continuity_guardian":
        match = re.search(
            r"END status=(OK|WARN|CRITICAL)",
            p.stdout,
            re.IGNORECASE,
        )
        if match:
            raw = match.group(1).upper()
            status = {
                "OK": "healthy",
                "WARN": "warning",
                "CRITICAL": "critical",
            }[raw]
        elif p.returncode != 0:
            status = "execution_failure"
        else:
            status = "execution_failure"

    else:
        status = "healthy" if p.returncode == 0 else "execution_failure"

    return {
        "component": component,
        "status": status,
        "ok": status == "healthy",
        "returncode": p.returncode,
        "stdout": stdout,
        "stderr": stderr,
    }


def verify_absorption_marker() -> dict:
    try:
        data = json.loads(ABSORB_MARKER.read_text())
        stamp = data.get("last_success_utc")
        if not stamp:
            raise ValueError("last_success_utc missing")

        stamp_dt = parse_utc(stamp)
        age_hours = (
            datetime.now(timezone.utc) - stamp_dt
        ).total_seconds() / 3600.0

        marker_status = data.get("status")
        if marker_status != "ok":
            health = "critical"
        elif age_hours > ABSORB_MAX_AGE_HOURS:
            health = "warning"
        else:
            health = "healthy"

        return {
            "component": "absorption_evidence",
            "status": health,
            "ok": health == "healthy",
            "source": str(ABSORB_MARKER),
            "last_success_utc": stamp,
            "age_hours": round(age_hours, 2),
            "max_age_hours": ABSORB_MAX_AGE_HOURS,
            "marker_status": marker_status,
        }

    except Exception as exc:
        return {
            "component": "absorption_evidence",
            "status": "critical",
            "ok": False,
            "source": str(ABSORB_MARKER),
            "error": f"{type(exc).__name__}: {exc}",
        }


def run_acs02() -> list[dict]:
    results: list[dict] = []

    worker = run_process("absorb_memory", ABSORB_WORKER)
    results.append(worker)

    if worker["status"] != "healthy":
        results.append({
            "component": "public_marker",
            "status": "execution_failure",
            "ok": False,
            "skipped": True,
            "reason": "absorption worker did not complete successfully",
        })
        return results

    marker = run_process(
        "write_absorption_public_marker",
        ABSORB_MARKER_WRITER,
    )
    results.append(marker)

    if marker["status"] != "healthy":
        return results

    results.append(verify_absorption_marker())
    return results


def overall_status(results: list[dict]) -> str:
    return max(
        (r.get("status", "execution_failure") for r in results),
        key=lambda s: SEVERITY.get(s, 3),
    )


def write_state(agent: str, started: str, results: list[dict]) -> dict:
    status = overall_status(results)

    payload = {
        "agent": agent,
        "started_at_utc": started,
        "finished_at_utc": now(),
        "status": status,
        "verified": True,
        "results": results,
    }

    STATE.mkdir(parents=True, exist_ok=True)
    target = STATE / f"{agent.lower().replace('-', '')}_state.json"
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n")
    os.replace(tmp, target)

    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "agent",
        choices=["ACS-02", "ACS-03", "ACS-04", "ACS-05"],
    )
    args = parser.parse_args()

    started = now()

    if args.agent == "ACS-02":
        results = run_acs02()
    else:
        results = []
        for component, path in CYCLES[args.agent]:
            if component == "continuity_guardian":
                extra = ["--force"]
            elif component == "infrastructure_guardian":
                # Allow only the guardian's explicitly configured safe repairs
                # (for example stale-lock removal and log rotation).
                extra = ["--apply"]
            else:
                extra = None
            results.append(run_process(component, path, extra))

    payload = write_state(args.agent, started, results)
    print(json.dumps(payload))

    return SEVERITY[payload["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
