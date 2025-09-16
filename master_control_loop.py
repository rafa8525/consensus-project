#!/usr/bin/env python3
"""
master_control_loop.py
Main loop that writes heartbeat + rotates agent tasks.
"""

import os
import time
import subprocess
from datetime import datetime

# Paths
LOG_FILE = "memory/logs/system/mcl_log.csv"
HEARTBEAT_FILE = "memory/logs/heartbeat/heartbeat.log"

# Agents/scripts to run in rotation (lightweight first)
TASKS = [
    ["python3", "agents_recommendation.py"],
    ["bash", "tools/runtime_prune.sh"],
    ["python3", "tools/github_sync.py"],  # adjust if named differently
    ["python3", "tools/backup_runner.py"],  # adjust if named differently
]

INTERVAL = 60  # seconds between cycles

def log(msg: str):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}", flush=True)

def write_heartbeat():
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(HEARTBEAT_FILE), exist_ok=True)
    with open(HEARTBEAT_FILE, "a", encoding="utf-8") as f:
        f.write(f"HEARTBEAT: {ts}\n")
    log("Heartbeat written.")

def run_task(task):
    """Run one agent task safely."""
    try:
        result = subprocess.run(task, capture_output=True, text=True, timeout=45)
        if result.returncode == 0:
            log(f"✅ Task {' '.join(task)} completed.")
        else:
            log(f"⚠️ Task {' '.join(task)} exited rc={result.returncode}.")
    except Exception as e:
        log(f"❌ Task {' '.join(task)} failed: {e}")

def main():
    log("🚀 Master Control Loop started.")
    i = 0
    while True:
        write_heartbeat()
        task = TASKS[i % len(TASKS)]
        run_task(task)
        i += 1
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
