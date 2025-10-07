#!/usr/bin/env python3
"""
Master Control Loop — Guard Supervisor
--------------------------------------
Purpose:
Continuously monitors and runs all core Consensus-Project tasks
in a controlled, fault-tolerant cycle.

Includes:
 • Knowledge-base verification
 • VPN test suite
 • Security audit
 • Fitness tracker
 • Memory manifest logger
 • Weekly status generator (Sunday)
 • Self-heal + logging

Location: /home/rafa1215/consensus-project/mcl_guard.py
"""

import subprocess, time, os, sys, traceback
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path("/home/rafa1215/consensus-project")
TOOLS = ROOT / "tools"
LOGS = ROOT / "memory" / "logs" / "system"
LOGS.mkdir(parents=True, exist_ok=True)
HEARTBEAT = LOGS / "mcl_guard_heartbeat.log"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TASKS = {
    # Hourly / frequent safety checks
    "verify_kb_permissions.py":   {"interval": 60 * 60},
    "log_memory_manifest.py":     {"interval": 60 * 60 * 6},

    # Daily tasks
    "fitness_tracker.py":         {"interval": 60 * 60 * 24, "run_at": "22:00"},

    # Weekly tasks
    "vpn_test_suite.py":          {"interval": 60 * 60 * 24 * 7, "run_on": "Mon"},
    "generate_weekly_status.py":  {"interval": 60 * 60 * 24 * 7, "run_on": "Sun"},

    # Monthly task
    "run_security_audit.py":      {"interval": 60 * 60 * 24 * 30, "run_day": 1},
}

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(HEARTBEAT, "a") as f:
        f.write(line + "\n")

def should_run(task, meta):
    """Determine whether to run a task based on day/time rules."""
    now = datetime.now()
    if "run_on" in meta and now.strftime("%a") != meta["run_on"]:
        return False
    if "run_day" in meta and now.day != meta["run_day"]:
        return False
    if "run_at" in meta:
        h, m = map(int, meta["run_at"].split(":"))
        if not (now.hour == h and now.minute >= m and now.minute < m + 10):
            return False
    last_file = LOGS / f".last_{task}"
    if last_file.exists():
        last_time = datetime.fromtimestamp(last_file.stat().st_mtime)
        if (now - last_time) < timedelta(seconds=meta["interval"]):
            return False
    last_file.touch()
    return True

def run_task(task):
    """Run a tool safely with error capture."""
    path = TOOLS / task
    if not path.exists():
        log(f"⚠️  Missing task: {task}")
        return
    try:
        cmd = [sys.executable, str(path)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        if result.returncode == 0:
            log(f"✅ {task} executed successfully")
        else:
            log(f"❌ {task} exited with code {result.returncode}")
            log(result.stderr.strip())
    except Exception as e:
        log(f"❌ Exception running {task}: {e}")
        traceback.print_exc(file=open(LOGS / "mcl_guard_errors.log", "a"))

# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------
def main():
    log("🔁 MCL Guard starting supervision cycle")
    while True:
        for task, meta in TASKS.items():
            if should_run(task, meta):
                run_task(task)
        # Heartbeat update
        log("💓 Guard heartbeat OK")
        time.sleep(60)  # check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🛑 Guard stopped manually")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        traceback.print_exc(file=open(LOGS / "mcl_guard_errors.log", "a"))
