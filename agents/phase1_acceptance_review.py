#!/usr/bin/env python3
"""Phase 1 fail-closed acceptance; no production changes by default."""
import argparse
import base64
import json
import os
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = "rafa8525/consensus-project"
REPORT = "logs/system/pythonanywhere_health.json"
ROOT = Path.home() / ".config/ai-consensus"
AGENTS = tuple("ACS-%02d" % i for i in range(1, 6))
HORIZON = timedelta(hours=36)
PROOF_HORIZON = timedelta(days=14)
NEEDED = 3

def timevalue(value):
    if not isinstance(value, str):
        return None
    try:
        v = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return v.astimezone(timezone.utc) if v.tzinfo else None
    except (ValueError, OverflowError):
        return None

def recent(value, now, horizon=HORIZON):
    t = timevalue(value)
    return t is not None and timedelta(0) <= now - t <= horizon

def evaluate(report, evidence, now=None):
    now = now or datetime.now(timezone.utc)
    if not isinstance(report, dict):
        return {"report_schema": False}
    checks = {"report_fresh": recent(report.get("generated_at_utc"), now)}
    agents = report.get("agents")
    agents = agents if isinstance(agents, dict) else {}
    for name in AGENTS:
        a = agents.get(name)
        a = a if isinstance(a, dict) else {}
        checks[name + "_healthy"] = (
            a.get("verified") is True and a.get("status") == "current"
            and a.get("health_status") in ("ok", "healthy")
        )
        checks[name + "_timestamp"] = recent(a.get("last_execution_utc"), now)
    sched = report.get("pythonanywhere_schedule")
    sched = sched if isinstance(sched, dict) else {}
    parent = sched.get("acs01_task")
    parent = parent if isinstance(parent, dict) else {}
    # ACS-01 is the scheduled parent and publishes the health bridge itself.
    checks["parent_schedule"] = sched.get("available") is True and parent.get("enabled") is True
    git = report.get("git")
    git = git if isinstance(git, dict) else {}
    reach = git.get("origin_reachable")
    checks["git_reachable"] = isinstance(reach, dict) and reach.get("ok") is True
    checks["no_merge_conflict"] = git.get("unresolved_merge_conflict") is False
    heal = report.get("self_heal")
    heal = heal if isinstance(heal, dict) else {}
    sync = heal.get("branch_sync")
    sync = sync if isinstance(sync, dict) else {}
    checks["branch_synced"] = (
        sync.get("ok") is True and sync.get("ahead_after") == 0
        and sync.get("behind_after") == 0
    )
    # Review evidence from actual tests; do not substitute bridge's narrow
    # observed-divergence flag, synthetic fixtures, or a simple success exit.
    tests = evidence.get("tests") if isinstance(evidence, dict) else None
    tests = tests if isinstance(tests, dict) else {}
    for key in ("failure_detection", "automatic_retry", "recovery_verified", "bounded_escalation"):
        item = tests.get(key)
        checks["proof_" + key] = (
            isinstance(item, dict) and item.get("passed") is True
            and isinstance(item.get("source"), str) and bool(item["source"].strip())
            and recent(item.get("executed_at_utc"), now, PROOF_HORIZON)
        )
    return checks

def fetch_remote():
    url = "https://api.github.com/repos/%s/contents/%s?ref=main" % (REPO, REPORT)
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github.raw+json",
        "Cache-Control": "no-cache", "User-Agent": "ACS-Phase1-Acceptance"
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        value = json.load(response)
    if isinstance(value, dict) and value.get("encoding") == "base64":
        value = json.loads(base64.b64decode(value["content"]))
    if not isinstance(value, dict):
        raise ValueError("Invalid remote payload")
    return value

def advance(report, evidence, history, now):
    checks = evaluate(report, evidence, now)
    passing = all(checks.values())
    stamp = report.get("generated_at_utc") if isinstance(report, dict) else None
    prior = history.get("passing_reports", []) if isinstance(history, dict) else []
    prior = prior if isinstance(prior, list) else []
    prior = [s for s in prior if timevalue(s)]
    if not passing:
        prior = []
    elif recent(stamp, now):
        if prior and timevalue(stamp) <= timevalue(prior[-1]):
            pass  # repeat or older snapshots cannot earn more credit
        else:
            if prior and timevalue(stamp) - timevalue(prior[-1]) > HORIZON:
                prior = []
            prior = (prior + [stamp])[-NEEDED:]
    return checks, prior, passing and len(prior) == NEEDED

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".phase1-")
    try:
        with os.fdopen(fd, "w") as fp:
            json.dump(data, fp, sort_keys=True, indent=2)
            fp.write("\n")
            fp.flush()
            os.fsync(fp.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--report-file", type=Path, help="Fixture for isolated tests only")
    ap.add_argument("--proof-file", type=Path, default=ROOT / "phase1_recovery_evidence.json")
    ap.add_argument("--state-dir", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    if args.record and args.report_file:
        print("FAIL: cannot record a fixture as production evidence")
        return 2
    now = datetime.now(timezone.utc)
    try:
        report = json.loads(args.report_file.read_text()) if args.report_file else fetch_remote()
        evidence = json.loads(args.proof_file.read_text())
    except (OSError, ValueError, TimeoutError, RuntimeError, urllib.error.URLError) as exc:
        print("FAIL: report/proof unavailable:", type(exc).__name__)
        return 1
    statefile = args.state_dir / "phase1_history.json"
    completefile = args.state_dir / "PHASE_1_COMPLETE.json"
    try:
        old = json.loads(statefile.read_text())
    except (OSError, ValueError):
        old = {}
    checks, reports, complete = advance(report, evidence, old, now)
    for k, ok in checks.items():
        print(("PASS" if ok else "FAIL") + ": " + k)
    print("Distinct passing reports:", len(reports), "/", NEEDED)
    print("Phase 1:", "COMPLETE" if complete else "NOT COMPLETE")
    if args.record:
        save(statefile, {"passing_reports": reports, "checked_at_utc": now.isoformat()})
        if complete:
            save(completefile, {
                "phase": 1, "status": "COMPLETE",
                "verified_at_utc": now.isoformat(),
                "reports": reports, "recovery_evidence_file": str(args.proof_file)
            })
        elif completefile.exists():
            completefile.unlink()
    return 0 if complete else 1

if __name__ == "__main__":
    sys.exit(main())
