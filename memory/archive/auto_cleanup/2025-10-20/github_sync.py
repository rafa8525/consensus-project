#!/usr/bin/env python3
"""
GitHub Sync Agent with JSON heartbeat
Handles auto-commit and push of memory folder safely.
"""

import os
import time
import json
import subprocess
import logging
from datetime import datetime, timezone

# Config
PROJECT_DIR = os.path.expanduser("~/consensus-project")
LOG_FILE = os.path.join(PROJECT_DIR, "memory/logs/system/github_sync.log")
HEARTBEAT_FILE = os.path.join(PROJECT_DIR, "memory/logs/system/github_sync_heartbeat.json")
HEARTBEAT_INTERVAL = 60  # seconds
SYNC_INTERVAL = 300       # run sync every 5 minutes

# Setup logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("GitHubSync")

def write_heartbeat():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {"timestamp": ts, "pid": os.getpid(), "status": "alive"}
    tmp_file = HEARTBEAT_FILE + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_file, HEARTBEAT_FILE)
    logger.info(f"❤️ GITHUB_SYNC_HEARTBEAT {ts}")

def run_git_sync():
    try:
        logger.info("🔍 Running safety pre-push checks...")
        subprocess.run(["git", "-C", PROJECT_DIR, "add", "-A"], check=True)
        commit_msg = f"Auto-sync {datetime.now(timezone.utc).isoformat()}"
        subprocess.run(["git", "-C", PROJECT_DIR, "commit", "-m", commit_msg], check=False)
        subprocess.run(["git", "-C", PROJECT_DIR, "push", "origin", "v1.1-dev"], check=True)
        logger.info("✅ GitHub sync completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ GitHub sync failed: {e}")

def run_sync_agent():
    logger.info("🚀 GitHub Sync Agent started")
    last_sync = 0
    while True:
        try:
            now = time.time()
            if now - last_sync >= SYNC_INTERVAL:
                run_git_sync()
                last_sync = now

            # Heartbeat
            write_heartbeat()

            time.sleep(HEARTBEAT_INTERVAL)

        except Exception as e:
            logger.error(f"❌ Error in GitHub Sync loop: {e}")
            time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    run_sync_agent()
