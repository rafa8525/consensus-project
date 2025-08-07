#!/usr/bin/env python3
import os
import subprocess
import datetime
from dotenv import load_dotenv

# Load credentials
load_dotenv()
GIT_USER = "rafa8525"
REPO = "https://github.com/rafa8525/consensus-project.git"
BRANCH = "v1.1-dev"
LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/git/git_sync_log.txt"
EXCLUDE_LOGS = [
    "memory/logs/heartbeat/full_memory_absorption.log"
]

def log(msg):
    timestamp = datetime.datetime.now().isoformat()
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

def run(cmd):
    log(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout: log(f"stdout: {result.stdout.strip()}")
    if result.stderr: log(f"stderr: {result.stderr.strip()}")
    return result

def git_sync():
    run("git pull origin v1.1-dev")
    run("git add -A")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Auto-log sync for {now}"
    run(f'git commit -m "{commit_msg}"')

    # Avoid large object errors by forcing smaller pack window
    run("git config pack.windowMemory 10m")
    run("git config pack.packSizeLimit 20m")

    push = run("git push origin v1.1-dev")
    if push.returncode == 0:
        log("✅ Git push completed successfully.")
    else:
        log("❌ Git push failed.")

if __name__ == "__main__":
    try:
        git_sync()
    except Exception as e:
        log(f"Unhandled exception: {str(e)}")
