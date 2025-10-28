#!/usr/bin/env python3
import os
import time
import json
import logging
from datetime import datetime, timezone

LOG_DIR = "memory/logs/system"
WORKER_LOG = os.path.join(LOG_DIR, "voice_worker.log")
HEARTBEAT_FILE = os.path.join(LOG_DIR, "voice_worker_heartbeat.json")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=WORKER_LOG,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def log_text_heartbeat():
    """Append a plain heartbeat line to the log with flush + fsync."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"HEARTBEAT: {ts}\n"
    with open(WORKER_LOG, "a", encoding="utf-8") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())
    logging.info(f"HEARTBEAT: {ts}")
    print(line.strip(), flush=True)

def log_json_heartbeat():
    """Write heartbeat as an atomic JSON file."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {"timestamp": ts, "pid": os.getpid(), "status": "alive"}
    tmp_file = HEARTBEAT_FILE + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_file, HEARTBEAT_FILE)  # atomic rename
    logging.info(f"❤️ VOICE_WORKER_HEARTBEAT {ts}")

def check_for_voice_trigger():
    """Stub: Replace with actual trigger detection logic."""
    logging.info("🎤 Checking for new voice trigger...")

def main():
    logging.info("🚀 voice_worker.py started")
    while True:
        try:
            check_for_voice_trigger()
            log_text_heartbeat()
            log_json_heartbeat()
            time.sleep(5)  # heartbeat interval
        except Exception as e:
            logging.error(f"Voice worker error: {e}", exc_info=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
