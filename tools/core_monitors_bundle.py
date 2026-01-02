#!/usr/bin/env python3
"""
core_monitors_bundle.py

Runs all core seed/monitor agents in sequence and logs their results.
Intended to be scheduled every 6 hours on PythonAnywhere.

Agents included:
- agents/absorption_runner_agent.py
- agents/absorption_monitor_agent.py
- agents/geofence_sms_seed_agent.py
- agents/geofence_sms_monitor_agent.py
- agents/gmail_activity_seed_agent.py
- agents/gmail_monitor_agent.py

Log file:
- memory/logs/system/core_monitors_bundle.log
"""

import datetime
from datetime import timezone
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "memory" / "logs" / "system"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "core_monitors_bundle.log"

AGENTS = [
    "agents/absorption_runner_agent.py",
    "agents/absorption_monitor_agent.py",
    "agents/geofence_sms_seed_agent.py",
    "agents/geofence_sms_monitor_agent.py",
    "agents/gmail_activity_seed_agent.py",
    "agents/gmail_monitor_agent.py",
]
# Mutation_b29d75


def utc_iso() -> str:
    """Return current UTC time as ISO 8601 string with timezone."""
    return datetime.datetime.now(timezone.utc).isoformat()


def log(message: str) -> None:
    timestamp = utc_iso()
    line = f"[{timestamp}] {message}\n"
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line)

# Mutation_99a694

def run_agent(script_rel_path: str) -> bool:
    script_path = PROJECT_ROOT / script_rel_path
    if not script_path.exists():
        log(f"ERROR: Script not found: {script_rel_path}")
        return False

    log(f"START: {script_rel_path}")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
    except Exception as exc:
        log(f"EXCEPTION: {script_rel_path}: {exc}")
        return False

    if result.stdout:
        log(f"STDOUT {script_rel_path}:\n{result.stdout.strip()}")
    if result.stderr:
        log(f"STDERR {script_rel_path}:\n{result.stderr.strip()}")

    if result.returncode == 0:
        log(f"SUCCESS: {script_rel_path} (exit {result.returncode})")
        return True
    else:
        log(f"FAILURE: {script_rel_path} (exit {result.returncode})")
        return False


def main() -> None:
    start_ts = utc_iso()
    log("=" * 80)
    log(f"Core monitors bundle run started at {start_ts}")

    successes = 0
    failures = 0
# Mutation_d415f0

    for agent in AGENTS:
        ok = run_agent(agent)
        if ok:
            successes += 1
        else:
            failures += 1

    end_ts = utc_iso()
    log(
        f"Core monitors bundle completed at {end_ts} "
        f"(successes={successes}, failures={failures})"
    )
# Mutation_cba411

    if failures > 0:
        # Non-zero exit so higher-level monitors or alerts can notice
        sys.exit(1)


if __name__ == "__main__":
    main()