#!/usr/bin/env python3
"""
voice_guard.py
Heartbeat-based supervisor for voice_worker.py
Safe for PythonAnywhere — will NOT close your console.
Logs results to memory/logs/system/voice_guard.md
"""

import os
import subprocess
import time
from datetime import datetime

# Config
HEARTBEAT_FILE = "memory/logs/heartbeat/voice_lookup_heartbeat.log"
LOG_FILE = "memory/logs/system/voice_guard.md"
VOICE_COMMAND = ["python3", "voice_worker.py"]
MAX_AGE_MINUTES = 10   # restart if heartbeat older than this
CHECK_INTERVAL = 60    # seconds

def log(msg: str):
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {msg}\n")

def heartbeat_is_stale():
    if not os.path.exists(HEARTBEAT_FILE):
        log("⚠️ No heartbeat file found.")
        return True
    mtime = datetime.fromtimestamp(os.path.getmtime(HEARTBEAT_FILE))
    age = datetime.now() - mtime
    if age.total_seconds() > MAX_AGE_MINUTES * 60:
        log(f"⚠️ Heartbeat stale (last update {mtime})")
        return True
    return False

def restart_voice_worker():
    try:
        log("🔄 Restarting voice_worker.py...")
        subprocess.Popen(VOICE_COMMAND)
        log("✅ voice_worker.py restarted successfully.")
    except Exception as e:
        log(f"❌ Failed to restart voice_worker.py: {e}")

def main():
    log("🚀 voice_guard.py started.")
    while True:
        if heartbeat_is_stale():
            restart_voice_worker()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
