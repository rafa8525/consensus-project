#!/usr/bin/env python3
import os
import time
import datetime
import subprocess

LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/system/skipped_task_recovery.log"

TASKS = [
    ("VPN Test", "/home/rafa1215/consensus-project/memory/tools/log_vpn_heartbeat.py"),
    ("GitHub Sync", "/home/rafa1215/consensus-project/memory/tools/log_github_heartbeat.py"),
    ("Fitness Log", "/home/rafa1215/consensus-project/memory/tools/log_fitness_heartbeat.py"),
]

def log(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} {msg}\n")
    print(f"{ts} {msg}")

def task_recently_ran(script_path, minutes=60):
    try:
        mtime = os.path.getmtime(script_path)
        last_run = datetime.datetime.fromtimestamp(mtime)
        return (datetime.datetime.now() - last_run).total_seconds() < (minutes * 60)
    except FileNotFoundError:
        return False

log("=== Skipped Task Recovery Agent Started ===")

while True:
    for name, script in TASKS:
        if not task_recently_ran(script):
            log(f"{name} missing or stale — running now.")
            try:
                subprocess.run(["python3", script], check=True)
            except Exception as e:
                log(f"Error running {name}: {e}")
        else:
            log(f"{name} is up to date.")
    time.sleep(600)  # check every 10 minutes
