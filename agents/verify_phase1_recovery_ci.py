#!/usr/bin/env python3
"""Run real isolated watchdog fault-injection, never touch live agents/schedules."""
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
installer = (ROOT / "agents/install_phase1_recovery.sh").read_text()
start = installer.index("code=r'''") + len("code=r'''")
end = installer.index("'''", start)
watchdog_source = installer[start:end]
ast.parse(watchdog_source)

with tempfile.TemporaryDirectory(prefix="acs-phase1-isolated-") as d:
    directory = Path(d)
    watchdog = directory / "recovery_watchdog.py"
    watchdog.write_text(watchdog_source)
    spec = importlib.util.spec_from_file_location("isolated_watchdog", watchdog)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    now = datetime.now(timezone.utc)
    def healthy():
        return {
            "generated_at_utc": now.isoformat(),
            "agents": {name: {"verified": True, "status": "current", "health_status": "healthy"}
                       for name in module.names},
            "pythonanywhere_schedule": {
                "available": True,
                "acs01_task": {"enabled": True},
                "health_task": {"enabled": True}
            },
            "self_heal": {
                "branch_sync": {"ok": True, "ahead_after": 0, "behind_after": 0},
                "post_sync_cycles": {"outcomes": {
                    "ACS-04": [{"ok": True}], "ACS-05": [{"ok": True}]}}
            }
        }
    assert module.validate(healthy()) == []
    bad = healthy()
    bad["agents"]["ACS-03"]["status"] = "stale"
    assert "ACS-03_unhealthy" in module.validate(bad)
    print("PASS: failure_detection")

    events = []
    module.read = healthy
    module.write = lambda event, **fields: events.append((event, fields))
    module.time.sleep = lambda seconds: None
    first = {"n": 0}
    def fail_once_then_recover(cmd, timeout=1200):
        assert cmd[0] == "bash"
        first["n"] += 1
        exit_code = 17 if first["n"] == 1 else 0
        proc = subprocess.run([sys.executable, "-c", f"import sys;sys.exit({exit_code})"],
                              check=False)
        return proc.returncode == 0
    module.execute = fail_once_then_recover
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    assert result == 0 and first["n"] == 2
    assert any(e == "recovery_needed" for e, _ in events)
    assert events[-1][0] == "healthy"
    print("PASS: automatic_retry")
    print("PASS: recovery_verified (isolated_simulation_only)")

    events.clear()
    attempts = {"n": 0}
    def always_fail(cmd, timeout=1200):
        assert cmd[0] == "bash"
        attempts["n"] += 1
        return False
    module.execute = always_fail
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.main()
    assert result == 2 and attempts["n"] == 3
    assert events[-1][0] == "escalation"
    print("PASS: bounded_escalation")

    # Produce immutable-to-this-CI-run bytes, downloadable from Actions.
    artifact = directory / "recovery_simulation_evidence.json"
    payload = {
        "scope": "isolated_simulation_only",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "watchdog_source_sha256": hashlib.sha256(watchdog_source.encode()).hexdigest(),
        "results": {
            "failure_detection": "PASS",
            "automatic_retry": "PASS",
            "recovery_verified": "PASS (isolated simulation only)",
            "bounded_escalation": "PASS"
        },
        "limitations": [
            "No PythonAnywhere schedule or production process modified",
            "Does not demonstrate real production process restart or external outage recovery"
        ]
    }
    output = ROOT / "phase1_recovery_simulation_evidence.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("Evidence:", output)
