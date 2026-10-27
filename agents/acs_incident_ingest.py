#!/usr/bin/env python3
"""Convert published ACS evidence into durable, assigned incident records.

Read-only with respect to agent runtime, Git, schedules, and credentials.
The incident journal is opt-in until the Repair #2 scheduler gate passes.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from agents.acs_incident_coordinator import update
except ModuleNotFoundError:
    from acs_incident_coordinator import update

AGENTS = tuple(f"ACS-{n:02d}" for n in range(1, 6))
GOOD_HEALTH = {"healthy", "ok"}
BAD_STATUSES = {"missing", "unverified", "unreadable", "stale", "degraded", "critical", "execution_failure"}


def collect(report):
    if not isinstance(report, dict) or not isinstance(report.get("agents"), dict):
        raise ValueError("invalid report")
    stamp = report.get("generated_at_utc")
    if not isinstance(stamp, str):
        raise ValueError("missing report timestamp")
    dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("report timestamp must include timezone")
    evidence = dt.astimezone(timezone.utc).isoformat()
    events = []
    for agent in AGENTS:
        data = report["agents"].get(agent)
        if not isinstance(data, dict):
            events.append((agent, "AGENT_MISSING", "critical", evidence))
            continue
        if data.get("verified") is not True:
            events.append((agent, "AGENT_UNVERIFIED", "degraded", evidence))
        status = str(data.get("status", "")).lower()
        health = str(data.get("health_status", "")).lower()
        if status != "current" or health not in GOOD_HEALTH:
            severity = "critical" if status in {"critical", "execution_failure", "missing", "stale"} or health in {"critical", "execution_failure"} else "degraded"
            events.append((agent, "AGENT_HEALTH_DEGRADED", severity, evidence))
        diagnostics = data.get("diagnostics")
        if isinstance(diagnostics, dict):
            for code in diagnostics.get("issue_codes", []):
                if isinstance(code, str) and code and len(code) <= 80 and all(c.isupper() or c.isdigit() or c == "_" for c in code):
                    events.append((agent, code, "warning", evidence))
            for finding in diagnostics.get("findings", []):
                if isinstance(finding, dict) and finding.get("repaired") is not True:
                    code = finding.get("code")
                    if isinstance(code, str) and code and len(code) <= 80 and all(c.isupper() or c.isdigit() or c == "_" for c in code):
                        events.append((agent, code, "critical" if finding.get("severity") == "critical" else "warning", evidence))
    schedule = report.get("pythonanywhere_schedule")
    for name, agent in (("acs01_task", "ACS-01"), ("health_task", "ACS-05")):
        task = schedule.get(name) if isinstance(schedule, dict) else None
        if not isinstance(task, dict) or task.get("found") is not True or task.get("enabled") is not True:
            events.append((agent, "SCHEDULE_" + name.upper() + "_UNAVAILABLE", "critical", evidence))
    return events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="logs/system/pythonanywhere_health.json")
    parser.add_argument("--state", default="memory/agents/acs_incidents.json")
    args = parser.parse_args()
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    events = collect(report)
    for agent, code, severity, stamp in events:
        update(args.state, agent, code, severity, stamp)
    print(json.dumps({"recorded": len(events), "state": args.state}))


if __name__ == "__main__":
    main()
