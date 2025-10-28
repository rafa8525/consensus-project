#!/usr/bin/env python3
"""
log_repair_guard.py
Purpose:
  Ensures all expected log files exist and are initialized.
  Automatically recreates any missing Gmail or Calendar log files.
"""

import datetime
from pathlib import Path

BASE = Path("/home/rafa1215/consensus-project")
LOG_DIRS = [
    BASE / "memory/logs/email",
    BASE / "memory/logs/calendar",
    BASE / "memory/logs/system",
    BASE / "memory/logs/voice",
]

EXPECTED_FILES = {
    "calendar": [
        "event_sync_guard.md",
        "event_creator.log",
        "voice_event_log.md",
    ],
    "email": [
        "connection_guard.md",
    ],
    "system": [
        "master_guard_integrator.log",
        "master_control_loop.log",
        "heartbeat.log",
    ],
    "voice": [
        "voice_connector_log.md",
        "voice_integration_log.md",
    ],
}

def ensure_logs():
    for log_dir in LOG_DIRS:
        log_dir.mkdir(parents=True, exist_ok=True)

    for category, files in EXPECTED_FILES.items():
        path = BASE / f"memory/logs/{category}"
        for fname in files:
            fpath = path / fname
            if not fpath.exists():
                with open(fpath, "w") as f:
                    f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] Created missing log file: {fname}\n")
                print(f"✅ Recreated missing log: {fpath}")

if __name__ == "__main__":
    ensure_logs()
    print("---- Log Repair Guard completed ----")
