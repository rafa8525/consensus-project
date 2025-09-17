#!/usr/bin/env python3
"""
mcl_guard.py - Guard for Master Control Loop and Integration Reporter

Monitors:
1. master_control_loop.py (Always-On)
2. integration_reporter.py (hourly)

Actions:
- Checks if processes are alive
- Verifies heartbeat/report freshness
- Restarts master_control_loop.py if missing or stale
- Logs all activity to memory/logs/system/mcl_guard.log
"""

import os
import sys
import time
import json
import subprocess
import logging
from datetime import datetime, timezone
from pathlib import Path

# === Config ===
PROJECT_DIR = os.path.expanduser("~/consensus-project")
LOG_FILE = os.path.join(PROJECT_DIR, "memory/logs/system/mcl_guard.log")

MCL_SCRIPT = "master_control_loop.py"
MCL_HEARTBEAT = os.path.join(PROJECT_DIR, "memory/logs/system/mcl_heartbeat.json")
MCL_TIMEOUT = 120  # seconds

INTEGRATION_REPORT = os.path.join(PROJECT_DIR, "memory/logs/system/integration_report.md")
REPORT_TIMEOUT = 3700  # ~1h + grace

SLEEP_INTERVAL = 30  # seconds between checks

# === Logging setup ===
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


# === Helpers ===
def read_json_heartbeat(path, timeout):
    """Check freshness of a JSON heartbeat file."""
    if not os.path.exists(path):
        return False, f"Missing {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        ts = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - ts).total_seconds()
        if age > timeout:
            return False, f"Stale ({age:.1f}s old)"
        return True, f"Fresh ({age:.1f}s old)"
    except Exception as e:
        return False, f"Error reading heartbeat: {e}"


def check_integration_report():
    """Verify integration_report.md is updated hourly."""
    if not os.path.exists(INTEGRATION_REPORT):
        return False, "Missing integration_report.md"
    try:
        mtime = os.path.getmtime(INTEGRATION_REPORT)
        age = time.time() - mtime
        if age > REPORT_TIMEOUT:
            return False, f"Report stale ({age:.1f}s old)"
        return True, f"Report fresh ({age:.1f}s old)"
    except Exception as e:
        return False, f"Error checking report: {e}"


def is_process_running(name):
    """Check if process with given script name is alive."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", name],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0 and bool(result.stdout.strip())
    except Exception as e:
        logger.error(f"Error checking process {name}: {e}")
        return False


def restart_process(script):
    """Restart a Python script in background."""
    try:
        logger.info(f"🔄 Restarting {script}...")
        subprocess.Popen(
            ["python3", os.path.join(PROJECT_DIR, script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        time.sleep(2)
        return is_process_running(script)
    except Exception as e:
        logger.error(f"Failed to restart {script}: {e}")
        return False


# === Main loop ===
def run():
    logger.info("🚀 mcl_guard.py started.")
    while True:
        # --- Check master_control_loop ---
        alive, msg = read_json_heartbeat(MCL_HEARTBEAT, MCL_TIMEOUT)
        if alive:
            logger.info(f"✅ master_control_loop healthy: {msg}")
        else:
            logger.warning(f"⚠️ master_control_loop issue: {msg}")
            if not is_process_running(MCL_SCRIPT):
                if restart_process(MCL_SCRIPT):
                    logger.info("✅ master_control_loop restarted successfully")
                else:
                    logger.error("❌ master_control_loop restart failed")

        # --- Check integration_reporter ---
        ok, msg = check_integration_report()
        if ok:
            logger.info(f"✅ Integration Reporter healthy: {msg}")
        else:
            logger.warning(f"⚠️ Integration Reporter issue: {msg}")

        time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        logger.info("mcl_guard.py stopped manually")
        sys.exit(0)
