#!/usr/bin/env python3
"""
master_control_loop.py
-------------------------------------------------
Safe skeleton Master Control Loop (MCL) for the
Consensus Project.

- Writes a heartbeat line every 60s
- Logs activity to memory/logs/system/mcl_log.csv
- Will not close your console
- Guard-friendly (no rc=2 exits)

Replace later with the full MCL logic when ready.
"""

import os
import time
from datetime import datetime

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HEARTBEAT_FILE = os.path.join(BASE_DIR, "memory/logs/heartbeat/heartbeat.log")
LOG_FILE = os.path.join(BASE_DIR, "memory/logs/system/mcl_log.csv")

# === Ensure log dirs exist ===
os.makedirs(os.path.dirname(HEARTBEAT_FILE), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(line: str):
    """Append a line to the MCL system log."""
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")

def write_heartbeat():
    """Append a heartbeat to the shared heartbeat file."""
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(HEARTBEAT_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] ❤️ MCL heartbeat alive\n")

def main():
    log("✅ MCL skeleton loop started.")
    while True:
        try:
            write_heartbeat()
            log("Heartbeat written.")
            time.sleep(60)  # 1 minute between heartbeats
        except Exception as e:
            log(f"⚠️ Error in loop: {e}")
            time.sleep(30)  # back off on error

if __name__ == "__main__":
    main()
