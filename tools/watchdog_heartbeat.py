#!/usr/bin/env python3
# Writes a heartbeat message to prove watchdog is still running

import os
from datetime import datetime

LOG_PATH = os.path.expanduser("~/consensus-project/memory/logs/system/watchdog_heartbeat.md")

def log_heartbeat():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] ✅ Watchdog is alive."
    with open(LOG_PATH, "a") as f:
        f.write(msg + "\n")
    print(msg)

if __name__ == "__main__":
    log_heartbeat()
