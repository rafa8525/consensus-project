#!/usr/bin/env python3
"""
absorb_guard.py
Hybrid version – combines freshness monitoring, escalation, and continuous operation.

Features:
- Monitors voice + fitness logs for staleness (>1h)
- Triggers full absorption via memory_auto_commit_merged.py
- Logs results to memory/logs/agents/memory_absorb_stub.log
- Escalates if 3 consecutive absorb attempts fail
- Runs continuously every 30 minutes
- Uses UTC-safe timestamps (no deprecation warnings)
"""

import os
import subprocess
import time
from datetime import datetime, timedelta, timezone

# === Configuration ===
VOICE_DIR = "/home/rafa1215/consensus-project/memory/logs/voice"
FITNESS_DIR = "/home/rafa1215/consensus-project/memory/logs/fitness"
LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/agents/memory_absorb_stub.log"
ESCALATION_STATE = "/home/rafa1215/consensus-project/memory/logs/agents/absorb_guard_state.txt"
ABSORB_CMD = ["python3", "/home/rafa1215/consensus-project/memory_auto_commit_merged.py"]
SLEEP_INTERVAL_MINUTES = 30

# === Helper Functions ===

def utc_now_str() -> str:
    """Return current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(message: str):
    """Append log message with UTC timestamp."""
    ts = utc_now_str()
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {message}\n")
    print(f"[{ts}] {message}")

def ensure_folder(path: str):
    """Ensure folder exists."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        log(f"Created missing folder: {path}")

def last_modified(path: str) -> datetime:
    """Return most recent modification time in a folder."""
    ensure_folder(path)
    try:
        mtimes = [os.path.getmtime(os.path.join(path, f)) for f in os.listdir(path)]
        return datetime.fromtimestamp(max(mtimes)) if mtimes else datetime.fromtimestamp(0)
    except Exception as e:
        log(f"Error scanning {path}: {e}")
        return datetime.fromtimestamp(0)

def run_absorb() -> bool:
    """Run the full absorption pipeline."""
    try:
        result = subprocess.run(ABSORB_CMD, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            log("Absorb pipeline succeeded.")
            return True
        else:
            log(f"Absorb pipeline failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        log(f"Absorb pipeline exception: {e}")
        return False

def get_fail_count() -> int:
    if not os.path.exists(ESCALATION_STATE):
        return 0
    with open(ESCALATION_STATE, "r") as f:
        try:
            return int(f.read().strip() or 0)
        except ValueError:
            return 0

def set_fail_count(count: int):
    os.makedirs(os.path.dirname(ESCALATION_STATE), exist_ok=True)
    with open(ESCALATION_STATE, "w") as f:
        f.write(str(count))

# === Main Guard Logic ===

def run_guard_cycle():
    now = datetime.now(timezone.utc)
    stale = []

    # Check monitored folders
    for folder in [VOICE_DIR, FITNESS_DIR]:
        last_mod = last_modified(folder)
        age = now - last_mod.astimezone(timezone.utc)
        if age > timedelta(hours=1):
            stale.append((folder, age))

    if not stale:
        log("All monitored folders fresh (<1h). No absorption needed.")
        set_fail_count(0)
        return

    log(f"Detected stale folders: {[(f, str(a)) for f,a in stale]}")
    ok = run_absorb()

    if ok:
        set_fail_count(0)
    else:
        fails = get_fail_count() + 1
        set_fail_count(fails)
        if fails >= 3:
            log("⚠️  3 consecutive absorb failures detected — SMS escalation required.")

def main():
    log("=== absorb_guard.py (hybrid version) started ===")
    while True:
        try:
            run_guard_cycle()
        except Exception as e:
            log(f"Unexpected exception in guard cycle: {e}")
        log(f"Sleeping {SLEEP_INTERVAL_MINUTES}m before next cycle...")
        time.sleep(SLEEP_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
