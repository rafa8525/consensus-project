#!/usr/bin/env python3
"""
MCL Guard - Monitors master_control_loop.py and github_sync.py

This script ensures both core services stay alive and healthy by:
1. Checking JSON heartbeat files for freshness
2. Falling back to log file parsing if JSON missing/invalid
3. Restarting processes intelligently (cooldowns + max retries)
4. Logging all activity to memory/logs/system/mcl_guard.log
"""

import os
import sys
import json
import time
import subprocess
import logging
from datetime import datetime, timezone
from pathlib import Path

# Config
SERVICES = {
    "master_control_loop.py": {
        "heartbeat": "memory/logs/system/mcl_heartbeat.json",
        "log": "memory/logs/system/mcl.log",
        "timeout": 90,  # seconds
    },
    "github_sync.py": {
        "heartbeat": "memory/logs/system/github_sync_heartbeat.json",
        "log": "memory/logs/system/github_sync.log",
        "timeout": 120,  # seconds
    }
}
GUARD_SLEEP_INTERVAL = 15
MAX_RESTART_ATTEMPTS = 3
RESTART_COOLDOWN = 30  # seconds

# Setup logging
os.makedirs("memory/logs/system", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("memory/logs/system/mcl_guard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MCL_Guard")


class ServiceGuard:
    def __init__(self, name, heartbeat, log, timeout):
        self.name = name
        self.heartbeat_file = Path(heartbeat)
        self.log_file = Path(log)
        self.timeout = timeout
        self.restart_attempts = 0
        self.last_restart_time = 0
        self.pid = None

    def read_json_heartbeat(self):
        try:
            if not self.heartbeat_file.exists():
                return None
            data = json.loads(self.heartbeat_file.read_text())
            ts_str = data.get("timestamp")
            if not ts_str:
                return None
            hb_time = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - hb_time).total_seconds()
            return {"age": age, "pid": data.get("pid"), "status": data.get("status")}
        except Exception as e:
            logger.debug(f"{self.name} JSON heartbeat error: {e}")
            return None

    def parse_log_heartbeat(self):
        try:
            if not self.log_file.exists():
                return None
            lines = self.log_file.read_text().splitlines()[-50:]
            for line in reversed(lines):
                if "HEARTBEAT:" in line:
                    ts_str = line.split("HEARTBEAT:")[-1].strip()
                    try:
                        hb_time = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        age = (datetime.now(timezone.utc) - hb_time).total_seconds()
                        return {"age": age, "pid": "unknown", "status": "alive"}
                    except Exception:
                        continue
            return None
        except Exception as e:
            logger.debug(f"{self.name} log parse error: {e}")
            return None

    def get_heartbeat(self):
        hb = self.read_json_heartbeat()
        if hb:
            return hb
        return self.parse_log_heartbeat()

    def is_running(self):
        try:
            result = subprocess.run(
                ["pgrep", "-f", self.name],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                self.pid = result.stdout.strip().split("\n")[0]
                return True
            self.pid = None
            return False
        except Exception as e:
            logger.error(f"Error checking {self.name} process: {e}")
            return False

    def can_restart(self):
        now = time.time()
        if now - self.last_restart_time < RESTART_COOLDOWN:
            return False
        if self.restart_attempts >= MAX_RESTART_ATTEMPTS:
            return False
        return True

    def restart(self):
        if not self.can_restart():
            return False
        try:
            subprocess.Popen(
                ["python3", self.name],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            self.restart_attempts += 1
            self.last_restart_time = time.time()
            logger.warning(f"{self.name} restarted (attempt {self.restart_attempts})")
            return True
        except Exception as e:
            logger.error(f"Failed to restart {self.name}: {e}")
            self.restart_attempts += 1
            self.last_restart_time = time.time()
            return False

    def check(self):
        hb = self.get_heartbeat()
        if not hb:
            if self.is_running():
                logger.warning(f"{self.name} running but no heartbeat")
                return "running_no_hb"
            else:
                logger.error(f"{self.name} not running - restarting")
                return "restarted" if self.restart() else "restart_failed"

        if hb["age"] > self.timeout:
            if self.is_running():
                logger.error(f"{self.name} heartbeat stale ({hb['age']:.1f}s)")
                return "hung"
            else:
                logger.error(f"{self.name} not running (stale heartbeat) - restarting")
                return "restarted" if self.restart() else "restart_failed"

        # Fresh heartbeat
        if self.restart_attempts > 0:
            self.restart_attempts = 0
        logger.info(f"{self.name} healthy (age {hb['age']:.1f}s)")
        return "healthy"


def main():
    guards = [ServiceGuard(name, **cfg) for name, cfg in SERVICES.items()]
    logger.info("🚀 MCL Guard started - monitoring core services")
    while True:
        for g in guards:
            g.check()
        time.sleep(GUARD_SLEEP_INTERVAL)


if __name__ == "__main__":
    main()
