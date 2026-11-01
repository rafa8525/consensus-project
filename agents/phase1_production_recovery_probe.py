#!/usr/bin/env python3
"""Non-disruptive test of real ACS-01 supervisor health-publication retry.

Runs on PythonAnywhere and exercises *the installed supervisor.main()* while
substituting ONLY the parent agent cycle with a known healthy result. The first
real launcher subprocess returns exit 17 through a temporary PATH wrapper;
the next launcher subprocess must invoke the actual bridge and publish a new
GitHub main health report. Does not kill agents, change schedules or alter
the supervisor source. Tests production publishing retry, NOT external
scheduler outage or a production agent crash.
"""
import base64
import hashlib
import importlib
import json
import os
import shlex
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
REPO = HOME / "consensus-project"
OUT = HOME / ".local/state/ai-consensus/phase1_supervisor_retry_result.json"
API_URL = ("https://api.github.com/repos/rafa8525/consensus-project/"
           "contents/logs/system/pythonanywhere_health.json?ref=main")
AGENTS = tuple("ACS-%02d" % i for i in range(1, 6))

def remote():
    request = urllib.request.Request(API_URL, headers={
        "User-Agent": "ACS-Phase1-Production-Retry-Test",
        "Accept": "application/vnd.github+json", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return payload["sha"], json.loads(base64.b64decode(payload["content"]))

def healthy(report):
    states = report.get("agents") if isinstance(report, dict) else None
    if not isinstance(states, dict):
        return False
    for name in AGENTS:
        a = states.get(name)
        if not isinstance(a, dict):
            return False
        if (a.get("verified") is not True or a.get("status") != "current"
                or a.get("health_status") not in ("ok", "healthy")):
            return False
    return True

def test():
    if "--self-test" in sys.argv:
        assert healthy({"agents": {a: {"status": "current",
                      "health_status": "healthy", "verified": True}
                      for a in AGENTS}})
        assert not healthy({"agents": {"ACS-01": {"verified": True}}})
        print("PASS: host test preflight")
        return 0
    if "--execute" not in sys.argv:
        print("Safe by default: use --execute only from PythonAnywhere")
        return 2
    now = datetime.now(timezone.utc)
    # Observed daily ACS-01 scheduled run near 18:00 UTC; prevent overlap.
    if (now.hour == 17 and now.minute >= 45) or (now.hour == 18 and now.minute < 20):
        print("BLOCKED: too close to ACS-01 scheduled run")
        return 2
    if not (REPO / "agents/run_pythonanywhere_health_bridge.sh").is_file():
        print("BLOCKED: missing installed bridge launcher")
        return 2
    old_sha, old_report = remote()
    if not healthy(old_report):
        print("BLOCKED: latest published agents are not all healthy")
        return 2
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    mod = importlib.import_module("agents.supervisor")
    source = Path(mod.__file__).resolve()
    if source != (REPO / "agents/supervisor.py").resolve():
        print("BLOCKED: unexpected supervisor module")
        return 2
    import inspect
    main_source = inspect.getsource(mod.main)
    if "run_pythonanywhere_health_bridge.sh" not in main_source or "bridge_attempts" not in main_source:
        print("BLOCKED: installed supervisor does not match expected retry design")
        return 2
    original = mod.Supervisor.safe_run
    # Simulate only the *successful orchestration result*. The health bridge
    # and its real GitHub publication/retry remain completely unmocked.
    def simulated_healthy_cycle(self):
        return {"ok": True, "result": {"status": "ok",
                "results": {"system_health": {"ok": True}}}}
    started = datetime.now(timezone.utc)
    with tempfile.TemporaryDirectory(prefix="acs-supervisor-retry-") as td:
        folder = Path(td)
        calls = folder / "bash-invocations"
        wrapper = folder / "bash"
        wrapper.write_text(
            "#!/bin/sh\n"
            "echo attempt >> " + shlex.quote(str(calls)) + "\n"
            "COUNT=$(wc -l < " + shlex.quote(str(calls)) + ")\n"
            "if [ \"$COUNT\" -eq 1 ]; then exit 17; fi\n"
            "exec /bin/bash \"$@\"\n")
        wrapper.chmod(0o700)
        before_path = os.environ.get("PATH", "")
        try:
            os.environ["PATH"] = td + os.pathsep + before_path
            mod.Supervisor.safe_run = simulated_healthy_cycle
            exit_code = mod.main()
        finally:
            mod.Supervisor.safe_run = original
            os.environ["PATH"] = before_path
        attempts = len(calls.read_text().splitlines()) if calls.exists() else 0

    new_sha, report = remote()
    published = report.get("generated_at_utc", "")
    try:
        stamp = datetime.fromisoformat(published.replace("Z", "+00:00"))
        fresh = stamp.tzinfo is not None and stamp >= started
    except (TypeError, ValueError, AttributeError):
        fresh = False
    passed = (exit_code == 0 and attempts == 2 and old_sha != new_sha
              and fresh and healthy(report))
    result = {
        "scope": "production_host_controlled_transient_bridge_failure",
        "supervisor_cycle": "simulated_healthy_not_real_agent_cycle",
        "bridge_execution": "real_production_launcher",
        "external_scheduler_outage_tested": False,
        "production_agent_crash_tested": False,
        "started_at_utc": started.isoformat(),
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": "PASS" if passed else "FAIL",
        "launcher_invocations": attempts,
        "supervisor_returncode": exit_code,
        "github_report_updated": old_sha != new_sha,
        "github_report_fresh": fresh,
        "github_report_timestamp_utc": published,
        "supervisor_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("Evidence saved to:", OUT)
    return 0 if passed else 1

if __name__ == "__main__":
    try:
        sys.exit(test())
    except Exception as exc:
        print("FAIL CLOSED:", type(exc).__name__, str(exc)[:200])
        sys.exit(1)
