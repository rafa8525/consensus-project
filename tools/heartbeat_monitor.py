#!/usr/bin/env python3
"""
heartbeat_monitor.py
--------------------
Checks that master_control_loop.py is still active and logging regularly.
- If heartbeat is missing > threshold, restarts the loop automatically.
- Sends an SMS alert (via verified Twilio sender) ONLY if it fails twice consecutively.
"""

import os
import time
import datetime
import subprocess
import sys

# ----------------------------------------------------
# Import Twilio send_sms from reminder-api
# ----------------------------------------------------
sys.path.append("/home/rafa1215/reminder-api")
from send_reminder import send_sms

# ----------------------------------------------------
# Paths and configuration
# ----------------------------------------------------
BASE_DIR = os.path.expanduser("~/consensus-project")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "master_control_loop.log")
SCRIPT_PATH = os.path.join(BASE_DIR, "tools/master_control_loop.py")
HEARTBEAT_LOG = os.path.join(LOG_DIR, "heartbeat_monitor.log")
FAIL_COUNTER_FILE = os.path.join(LOG_DIR, "heartbeat_fail_count.txt")

THRESHOLD_MINUTES = 20   # restart if no heartbeat in 20 minutes
CHECK_INTERVAL_SECONDS = 3600  # run check every hour

# ----------------------------------------------------
# Helpers
# ----------------------------------------------------
def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(line + "\n")

def get_last_activity_minutes():
    if not os.path.exists(LOG_FILE):
        return None
    mtime = os.path.getmtime(LOG_FILE)
    delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(mtime)
    return delta.total_seconds() / 60

def read_fail_count():
    try:
        with open(FAIL_COUNTER_FILE) as f:
            return int(f.read().strip())
    except Exception:
        return 0

def write_fail_count(count):
    with open(FAIL_COUNTER_FILE, "w") as f:
        f.write(str(count))

def restart_master_loop():
    log("⚠️ No recent heartbeat detected — restarting master_control_loop.py...")
    try:
        subprocess.Popen(["/usr/bin/python3", SCRIPT_PATH])
        log("✅ Restart command issued successfully.")
    except Exception as e:
        log(f"❌ Failed to restart master_control_loop.py: {e}")

# ----------------------------------------------------
# Main Monitor Loop
# ----------------------------------------------------
def main():
    log("==== Heartbeat Monitor Started ====")
    while True:
        mins = get_last_activity_minutes()
        fails = read_fail_count()

        if mins is None:
            log("❌ master_control_loop.log not found; restarting loop.")
            restart_master_loop()
            fails += 1

        elif mins > THRESHOLD_MINUTES:
            log(f"❌ Last activity {mins:.1f} minutes ago — restarting loop.")
            restart_master_loop()
            fails += 1

        else:
            log(f"💓 Heartbeat healthy. Last activity {mins:.1f} min ago.")
            fails = 0  # reset after success

        # ------------------------------------------------
        # Alert logic: only send if two consecutive failures
        # ------------------------------------------------
        if fails >= 2:
            alert = (
                f"⚠️ ALERT: master_control_loop inactive for {mins:.1f if mins else 0} minutes.\n"
                f"Restart attempted twice — manual inspection recommended."
            )
            send_sms(alert)
            log(f"🚨 ALERT SENT: {alert}")
            fails = 0  # reset after alert to prevent repeat texts

        write_fail_count(fails)
        time.sleep(CHECK_INTERVAL_SECONDS)

# ----------------------------------------------------
if __name__ == "__main__":
    main()
