#!/usr/bin/env python3
"""Read-only Phase 1 deployment preflight. Never writes schedules, repo, or state."""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "consensus-project"
STATE = Path.home() / ".local/state/ai-consensus"
URL = ("https://raw.githubusercontent.com/rafa8525/consensus-project/"
       "main/logs/system/pythonanywhere_health.json")
NAMES = tuple("ACS-%02d" % i for i in range(1, 6))


def check_report(report):
    errors = []
    stamp = report.get("generated_at_utc")
    try:
        when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - when).total_seconds()
        if when.tzinfo is None or not 0 <= age <= 36 * 3600:
            errors.append("report_not_fresh")
    except (AttributeError, TypeError, ValueError):
        errors.append("report_bad_timestamp")
    agents = report.get("agents")
    agents = agents if isinstance(agents, dict) else {}
    for name in NAMES:
        agent = agents.get(name)
        if not isinstance(agent, dict) or not (
                agent.get("verified") is True
                and agent.get("status") == "current"
                and agent.get("health_status") in ("ok", "healthy")):
            errors.append(name + "_not_verified_healthy")
    sched = report.get("pythonanywhere_schedule") or {}
    health_task = sched.get("health_task") or {}
    parent = sched.get("acs01_task") or {}
    if not sched.get("available") or not parent.get("enabled"):
        errors.append("parent_schedule_not_confirmed")
    if health_task.get("mode") != "acs01_integrated" or not health_task.get("integrated_wiring_verified"):
        errors.append("unexpected_health_publisher_architecture")
    if health_task.get("standalone_found"):
        errors.append("standalone_schedule_detected")
    ids = health_task.get("matching_task_ids")
    if ids != [1524414]:
        errors.append("unexpected_parent_task_id")
    return errors


def main():
    print("READ-ONLY PHASE 1 PREFLIGHT")
    print("No schedule updates, agent runs, retries, or Git changes.")
    checks = {
        "repo_present": ROOT.is_dir(),
        "supervisor_present": (ROOT / "agents/supervisor.py").is_file(),
        "parent_launcher_present": (ROOT / "agents/run_acs01_supervisor.sh").is_file(),
        "publisher_present": (ROOT / "agents/run_pythonanywhere_health_bridge.sh").is_file(),
        "bridge_retry_evidence_present": (STATE / "phase1_supervisor_retry_result.json").is_file(),
        "controlled_escalation_evidence_present": (STATE / "phase1_host_controlled_escalation.json").is_file(),
    }
    try:
        proc = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT,
                              capture_output=True, text=True, timeout=10, check=False)
        branch = proc.stdout.strip()
        checks["expected_live_branch"] = proc.returncode == 0 and branch == "v1.1-dev"
        print("Local branch:", branch or "(unavailable)")
    except (OSError, subprocess.TimeoutExpired):
        checks["expected_live_branch"] = False
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "ACS-Phase1-ReadOnly-Preflight"})
        with urllib.request.urlopen(req, timeout=30) as response:
            report = json.load(response)
        errors = check_report(report)
        checks["remote_snapshot_healthy"] = not errors
        print("Latest published snapshot:", report.get("generated_at_utc"))
        print("Publisher architecture checks:", ", ".join(errors) if errors else "PASS")
        proof = (report.get("self_heal") or {}).get("recovery_proof") or {}
        checks["real_production_recovery_proven"] = proof.get("verified") is True
        print("Production recovery proof verified:", checks["real_production_recovery_proven"])
    except Exception as exc:
        checks["remote_snapshot_healthy"] = False
        checks["real_production_recovery_proven"] = False
        print("Remote snapshot read failed:", type(exc).__name__)
    for key, passed in checks.items():
        print(("PASS" if passed else "NOT VERIFIED") + ": " + key)
    preflight = all(v for k,v in checks.items() if k != "real_production_recovery_proven")
    print("Deployment preflight:", "PASS" if preflight else "BLOCKED")
    print("Phase 1 certified:", "NO (independent outage proof and gate still required)")
    return 0 if preflight else 2


if __name__ == "__main__":
    sys.exit(main())
