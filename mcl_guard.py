#!/usr/bin/env python3
"""
mcl_guard.py
Heartbeat-based supervisor for the Master Control Loop (MCL).
Now with extended logging of loop launches, exits, and restarts.
"""

import os
import subprocess
import time
from datetime import datetime, timedelta

# Config
HEARTBEAT_FILE = "memory/logs/heartbeat/heartbeat.log"
LOG_FILE = "memory/logs/system/mcl_guard.md"
MCL_COMMAND = ["python3", "master_control_loop.py"]
MAX_AGE_MINUTES = 10   # heartbeat staleness threshold
CHECK_INTERVAL = 60    # seconds between checks

process = None


def log(msg: str):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}", flush=True)


def heartbeat_is_stale() -> bool:
    if not os.path.exists(HEARTBEAT_FILE):
        log("⚠️ No heartbeat file found.")
        return True
    mtime = datetime.fromtimestamp(os.path.getmtime(HEARTBEAT_FILE))
    if datetime.utcnow() - mtime > timedelta(minutes=MAX_AGE_MINUTES):
        log(f"⚠️ Heartbeat stale (last update {mtime}).")
        return True
    return False


def restart_mcl():
    global process
    if process and process.poll() is None:
        process.terminate()
        log("⚠️ Terminated existing loop before restart.")

    try:
        log(f"🔄 Launching: {' '.join(MCL_COMMAND)}")
        process = subprocess.Popen(MCL_COMMAND)
        log(f"✅ Spawned master_control_loop.py pid={process.pid}")
    except Exception as e:
        log(f"❌ Failed to launch MCL: {e}")


def main():
    log("🚀 mcl_guard.py started.")
    restart_mcl()

    while True:
        time.sleep(CHECK_INTERVAL)

        # If the process is gone, restart it
        if process and process.poll() is not None:
            log(f"⚠️ Loop exited rc={process.returncode}, restarting...")
            restart_mcl()
            continue

        # If heartbeat stale, restart it
        if heartbeat_is_stale():
            log("⚠️ Restarting loop due to stale heartbeat...")
            restart_mcl()
        else:
            log("✅ Loop alive, heartbeat fresh.")


if __name__ == "__main__":
    main()
