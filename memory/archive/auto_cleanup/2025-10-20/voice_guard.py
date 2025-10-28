#!/usr/bin/env python3
"""
Voice Guard - Robust Process Monitor for voice_worker.py

This script monitors the voice_worker.py process by:
1. Primarily checking JSON heartbeat file (voice_worker_heartbeat.json)
2. Falling back to log file parsing only if JSON is missing/invalid
3. Restarting the worker only when heartbeat is actually stale (>60 seconds)
4. Eliminating parsing errors from mixed log content

Author: Generated for PythonAnywhere voice trigger system
"""

import os
import sys
import json
import time
import subprocess
import logging
from datetime import datetime, timezone
from pathlib import Path

# Configuration
HEARTBEAT_FILE = "memory/logs/system/voice_worker_heartbeat.json"
LOG_FILE = "memory/logs/system/voice_worker.log"
WORKER_SCRIPT = "voice_worker.py"
GUARD_LOG = "memory/logs/system/voice_guard.md"

HEARTBEAT_TIMEOUT_SECONDS = 60  # Consider heartbeat stale after 60 seconds
GUARD_SLEEP_INTERVAL = 10       # Check every 10 seconds
MAX_RESTART_ATTEMPTS = 3        # Maximum consecutive restart attempts
RESTART_COOLDOWN = 30           # Seconds to wait between restart attempts

# Setup logging
os.makedirs(os.path.dirname(GUARD_LOG), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(GUARD_LOG),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VoiceGuard:
    def __init__(self):
        self.restart_attempts = 0
        self.last_restart_time = 0
        self.worker_pid = None

    def read_json_heartbeat(self):
        try:
            heartbeat_path = Path(HEARTBEAT_FILE)
            if not heartbeat_path.exists():
                return None

            file_stat = heartbeat_path.stat()
            file_age = time.time() - file_stat.st_mtime
            if file_age > (HEARTBEAT_TIMEOUT_SECONDS * 2):
                logger.warning(f"JSON heartbeat file is very old ({file_age:.1f}s), likely stale")
                return None

            with open(heartbeat_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            required_fields = ["timestamp", "pid", "status"]
            if not all(field in data for field in required_fields):
                return None

            heartbeat_time = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
            current_time = datetime.now(timezone.utc)
            heartbeat_age = (current_time - heartbeat_time).total_seconds()
            data["age_seconds"] = heartbeat_age
            return data
        except Exception:
            return None

    def parse_log_heartbeat(self):
        try:
            log_path = Path(LOG_FILE)
            if not log_path.exists():
                return None

            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in reversed(lines[-50:]):
                if "HEARTBEAT:" in line:
                    try:
                        ts_str = line.split("HEARTBEAT:")[1].strip()
                        hb_time = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        current_time = datetime.now(timezone.utc)
                        age = (current_time - hb_time).total_seconds()
                        return {"timestamp": ts_str, "age_seconds": age, "source": "log_file"}
                    except Exception:
                        continue
            return None
        except Exception:
            return None

    def get_worker_heartbeat(self):
        hb = self.read_json_heartbeat()
        if hb is not None:
            hb["source"] = "json_file"
            return hb
        return self.parse_log_heartbeat()

    def is_worker_running(self):
        try:
            result = subprocess.run(
                ["pgrep", "-f", WORKER_SCRIPT],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                self.worker_pid = result.stdout.strip().split("\n")[0]
                return True
            self.worker_pid = None
            return False
        except Exception:
            return False

    def can_restart_worker(self):
        now = time.time()
        if now - self.last_restart_time < RESTART_COOLDOWN:
            return False
        if self.restart_attempts >= MAX_RESTART_ATTEMPTS:
            return False
        return True

    def start_worker(self):
        try:
            if not self.can_restart_worker():
                return False
            subprocess.Popen(
                ["python3", WORKER_SCRIPT],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            time.sleep(2)
            if self.is_worker_running():
                self.restart_attempts += 1
                self.last_restart_time = time.time()
                logger.info(f"✅ voice_worker.py started successfully (PID: {self.worker_pid})")
                return True
            else:
                self.restart_attempts += 1
                self.last_restart_time = time.time()
                logger.error("❌ voice_worker.py failed to start or died immediately")
                return False
        except Exception as e:
            logger.error(f"Error starting worker: {e}")
            self.restart_attempts += 1
            self.last_restart_time = time.time()
            return False

    def check_and_maintain_worker(self):
        hb = self.get_worker_heartbeat()
        if hb is None:
            if self.is_worker_running():
                logger.warning("⚠️ Worker running but no heartbeat")
                return
            logger.error("❌ No worker + no heartbeat. Restarting...")
            self.start_worker()
            return

        if hb["age_seconds"] > HEARTBEAT_TIMEOUT_SECONDS:
            logger.warning(f"⚠️ Heartbeat stale ({hb['age_seconds']:.1f}s)")
            if self.is_worker_running():
                logger.error("Worker running but unresponsive (hung).")
            else:
                logger.error("Worker not running. Restarting...")
                self.start_worker()
        else:
            self.restart_attempts = 0
            logger.info(f"✅ Worker healthy (heartbeat {hb['age_seconds']:.1f}s old from {hb['source']})")

    def run(self):
        logger.info("🚀 voice_guard.py started.")
        os.makedirs(os.path.dirname(HEARTBEAT_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

        while True:
            try:
                self.check_and_maintain_worker()
                time.sleep(GUARD_SLEEP_INTERVAL)
            except KeyboardInterrupt:
                logger.info("🛑 voice_guard.py interrupted, exiting.")
                break
            except Exception as e:
                logger.error(f"Loop error: {e}")
                time.sleep(GUARD_SLEEP_INTERVAL)

def main():
    guard = VoiceGuard()
    guard.run()

if __name__ == "__main__":
    main()
