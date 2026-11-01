#!/usr/bin/env python3
"""Controlled transient launcher failure against installed PythonAnywhere watchdog.

Runs the actual installed watchdog and production health bridge once, with the
first 'bash launcher' invocation intentionally returning 17 via a private PATH
wrapper. It does not alter schedules, source files, or stop existing agents.
REQUIRES: PythonAnywhere shell execution; never run automatically via GitHub CI.
It proves transient launcher recovery on a production host, NOT recovery from
an external PythonAnywhere scheduler outage.
"""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import shlex
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
REPO = HOME / "consensus-project"
WATCHDOG = HOME / ".config/ai-consensus/recovery_watchdog.py"
EVIDENCE = HOME / ".local/state/ai-consensus"
API_URL = (
    "https://api.github.com/repos/rafa8525/consensus-project/contents/"
    "logs/system/pythonanywhere_health.json?ref=main"
)
AGENTS = tuple("ACS-%02d" % i for i in range(1, 6))

def remote():
    req = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "ACS-Phase1-Production-Probe",
                 "Accept": "application/vnd.github+json",
                 "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
    report = json.loads(base64.b64decode(payload["content"]))
    return payload["sha"], report

def good(report):
    if not isinstance(report, dict):
        return False
    agents = report.get("agents")
    if not isinstance(agents, dict):
        return False
    for name in AGENTS:
        state = agents.get(name)
        if not isinstance(state, dict):
            return False
        if state.get("verified") is not True or state.get("status") != "current":
            return False
        if state.get("health_status") not in ("ok", "healthy"):
            return False
    return True

def load_watchdog():
    if not WATCHDOG.is_file():
        raise RuntimeError("Installed recovery watchdog missing; no test performed")
    spec = importlib.util.spec_from_file_location("acs_production_recovery", WATCHDOG)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import installed watchdog")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not all(hasattr(module, x) for x in ("main", "read", "validate", "log", "launch")):
        raise RuntimeError("Installed watchdog API differs; no test performed")
    if Path(module.launch).resolve() != (REPO / "agents/run_pythonanywhere_health_bridge.sh").resolve():
        raise RuntimeError("Unexpected launcher path; no test performed")
    return module

def main():
    if "--self-test" in sys.argv:
        assert good({"agents": {n: {"verified": True, "status": "current",
                    "health_status": "healthy"} for n in AGENTS}})
        assert not good({"agents": {"ACS-01": {"verified": True}}})
        print("PASS: production probe static preflight")
        return 0
    if "--execute" not in sys.argv:
        print("Dry run only; pass --execute on PythonAnywhere to run controlled test")
        return 2
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc)
    # Based on observed 18:00 UTC daily supervisor task: don't overlap it.
    if timestamp.hour == 17 and timestamp.minute >= 45:
        print("BLOCKED: near supervisor's daily UTC schedule")
        return 2
    if timestamp.hour == 18 and timestamp.minute < 20:
        print("BLOCKED: near supervisor's daily UTC schedule")
        return 2
    module = load_watchdog()
    old_sha, old_report = remote()
    if not good(old_report):
        print("BLOCKED: published agents not all healthy")
        return 2
    # The installed watchdog expects a report younger than 30 minutes.
    # A controlled normal refresh is allowed; it does not alter schedules.
    validation = module.validate(old_report)
    if validation == ["report_stale"]:
        normal = __import__("subprocess").run(
            ["/bin/bash", str(module.launch)], cwd=REPO, timeout=900,
            capture_output=True, text=True, check=False
        )
        if normal.returncode != 0:
            print("BLOCKED: baseline bridge refresh failed:", normal.returncode)
            return 2
        old_sha, old_report = remote()
        validation = module.validate(old_report)
    if validation:
        print("BLOCKED: installed watchdog preflight fails", validation)
        return 2

    result = {
        "scope": "production_host_controlled_launcher_failure",
        "started_at_utc": timestamp.isoformat(),
        "watchdog_sha256": hashlib.sha256(WATCHDOG.read_bytes()).hexdigest(),
        "initial_remote_blob_sha": old_sha,
        "production_scheduler_outage_tested": False,
        "production_agent_crash_tested": False,
    }
    exit_code = 1
    with tempfile.TemporaryDirectory(prefix="acs-phase1-probe-") as td:
        folder = Path(td)
        calls = folder / "calls"
        shell = folder / "bash"
        real_bash = "/bin/bash"
        if not Path(real_bash).is_file():
            raise RuntimeError("Expected /bin/bash missing")
        script = (
            "#!/bin/sh\n"
            "echo invocation >> " + shlex.quote(str(calls)) + "\n"
            "COUNT=$(wc -l < " + shlex.quote(str(calls)) + ")\n"
            "if [ \"$COUNT\" -eq 1 ]; then exit 17; fi\n"
            "exec " + shlex.quote(real_bash) + " \"$@\"\n"
        )
        shell.write_text(script)
        shell.chmod(0o700)
        module.log = EVIDENCE / "phase1_production_probe_events.jsonl"
        previous_path = os.environ.get("PATH", "")
        try:
            os.environ["PATH"] = td + os.pathsep + previous_path
            exit_code = module.main()
        finally:
            os.environ["PATH"] = previous_path
        count = len(calls.read_text().splitlines()) if calls.exists() else 0

    new_sha, new_report = remote()
    new_time = str(new_report.get("generated_at_utc", ""))
    try:
        posted = datetime.fromisoformat(new_time.replace("Z", "+00:00"))
        published_new = posted.tzinfo is not None and posted >= timestamp
    except ValueError:
        published_new = False
    passed = (exit_code == 0 and count == 2 and new_sha != old_sha
              and published_new and good(new_report))
    result.update({
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": "PASS" if passed else "FAIL",
        "watchdog_returncode": exit_code,
        "launcher_invocations": count,
        "published_new_remote_report": published_new,
        "final_remote_blob_sha": new_sha,
        "final_report_generated_at_utc": new_time,
    })
    path = EVIDENCE / "phase1_production_probe_result.json"
    path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True, indent=2))
    print("Evidence:", path)
    return 0 if passed else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("FAIL CLOSED:", type(exc).__name__, str(exc)[:200])
        sys.exit(1)
