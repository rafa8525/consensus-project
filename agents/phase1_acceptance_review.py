#!/usr/bin/env python3
"""Read-only Phase 1 acceptance review for the actual ACS-01 parent architecture.

Does not restart agents, touch Git state, or write a completion marker.
Exit 0: observed operational gate passes; exit 1: required evidence fails.
Recovery simulation and sustained unattended-run proof are reviewed separately.
"""
import json
import sys
import urllib.request
from datetime import datetime, timezone

URL = ("https://raw.githubusercontent.com/rafa8525/consensus-project/main/"
       "logs/system/pythonanywhere_health.json")
AGENTS = tuple(f"ACS-{i:02d}" for i in range(1, 6))
MAX_REPORT_AGE = 36 * 60 * 60

def evaluate(report, now=None):
    now = now or datetime.now(timezone.utc)
    findings = {}
    try:
        published = datetime.fromisoformat(
            report["generated_at_utc"].replace("Z", "+00:00")
        )
        if published.tzinfo is None:
            raise ValueError("naive timestamp")
        age = (now - published).total_seconds()
        findings["fresh_report"] = 0 <= age <= MAX_REPORT_AGE
    except (KeyError, TypeError, ValueError, AttributeError):
        findings["fresh_report"] = False

    agents = report.get("agents") or {}
    for name in AGENTS:
        state = agents.get(name) or {}
        findings[name] = (
            state.get("verified") is True
            and state.get("status") == "current"
            and state.get("health_status") in ("ok", "healthy")
        )
    schedule = report.get("pythonanywhere_schedule") or {}
    # The ACS-01 parent runs the health bridge after its own cycle.
    # A second health task is not required by this architecture.
    findings["supervisor_scheduled"] = (
        schedule.get("available") is True
        and (schedule.get("acs01_task") or {}).get("enabled") is True
    )
    git = report.get("git") or {}
    findings["git_reachable"] = (git.get("origin_reachable") or {}).get("ok") is True
    findings["no_merge_conflicts"] = git.get("unresolved_merge_conflict") is False
    sync = (report.get("self_heal") or {}).get("branch_sync") or {}
    findings["branch_synchronized"] = (
        sync.get("ok") is True
        and sync.get("ahead_after") == 0
        and sync.get("behind_after") == 0
    )
    return findings

def main():
    if "--self-test" in sys.argv:
        now = datetime.now(timezone.utc)
        report = {
            "generated_at_utc": now.isoformat(),
            "agents": {n: {"verified": True, "status": "current",
                           "health_status": "healthy"} for n in AGENTS},
            "pythonanywhere_schedule": {
                "available": True, "acs01_task": {"enabled": True},
                "health_task": {"enabled": False}
            },
            "git": {"origin_reachable": {"ok": True},
                    "unresolved_merge_conflict": False,
                    "status": {"tracked_changes_count": 22}},
            "self_heal": {"branch_sync": {
                "ok": True, "ahead_after": 0, "behind_after": 0
            }}
        }
        assert all(evaluate(report, now).values())
        report["agents"]["ACS-03"]["status"] = "stale"
        assert evaluate(report, now)["ACS-03"] is False
        report["agents"]["ACS-03"]["status"] = "current"
        report["pythonanywhere_schedule"]["acs01_task"]["enabled"] = False
        assert evaluate(report, now)["supervisor_scheduled"] is False
        report["pythonanywhere_schedule"]["acs01_task"]["enabled"] = True
        report["generated_at_utc"] = "2020-01-01T00:00:00+00:00"
        assert evaluate(report, now)["fresh_report"] is False
        print("PASS: parent scheduler, stale report and failed-agent cases")
        return 0

    req = urllib.request.Request(URL, headers={"User-Agent": "ACS-Phase1-Acceptance"})
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            report = json.load(res)
    except Exception as exc:
        print("FAIL: cannot retrieve public health report:", type(exc).__name__)
        return 1

    findings = evaluate(report)
    for key, passed in findings.items():
        print(("PASS" if passed else "FAIL") + ": " + key)
    print("Report timestamp:", report.get("generated_at_utc"))
    print("Recovery fault-injection proof: SEPARATE EVIDENCE REQUIRED")
    print("Unattended consecutive-run proof: SEPARATE EVIDENCE REQUIRED")
    print("Phase 1 is NOT marked complete by this operational check.")
    return 0 if all(findings.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
