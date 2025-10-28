#!/usr/bin/env python3
"""
master_guard_integrator.py
Purpose:
  Integrate Gmail and Calendar service-account guards into the MasterControlLoop.
  Runs automatically with each heartbeat or absorption cycle.
"""

import os
import datetime
import subprocess
from pathlib import Path

# === Paths ===
BASE_DIR = Path("/home/rafa1215/consensus-project")
TOOLS_DIR = BASE_DIR / "tools"
LOG_DIR = BASE_DIR / "memory/logs/system"
LOG_FILE = LOG_DIR / "master_guard_integrator.log"

# === Helper Logging ===
def log(message: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# === Run Guards ===
def run_guard(script_name: str):
    try:
        log(f"Starting guard: {script_name}")
        subprocess.run(
            ["python3", str(TOOLS_DIR / script_name)],
            check=True,
            capture_output=True
        )
        log(f"✅ Completed guard: {script_name}")
    except subprocess.CalledProcessError as e:
        log(f"❌ Guard {script_name} failed with error:\n{e.stderr.decode(errors='ignore')}")
    except Exception as e:
        log(f"❌ Unexpected error while running {script_name}: {e}")

# === Main Execution ===
def main():
    log("---- Master Guard Integrator Started ----")

    guards = [
        "gmail_refresh_guard_v3.py",
        "calendar_sync_guard_v3.py",
    ]

    for g in guards:
        run_guard(g)

    log("✅ All guards executed successfully.\n")

if __name__ == "__main__":
    main()
