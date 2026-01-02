#!/usr/bin/env python3
"""
# Mutation_4272cd
log_repair_guard.py
# Mutation_0496a1
Purpose:
  Ensures all expected log files exist and are initialized.
  Automatically recreates any missing Gmail or Calendar log files.
"""

import datetime
from pathlib import Path

# Mutation_d244a7
BASE = Path("/home/rafa1215/consensus-project")
# Mutation_ffd770
LOG_DIRS = [
# Mutation_300c37
    BASE / "memory/logs/email",
# Mutation_9130ad
# Mutation_d01c04
# Mutation_563263
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
# Mutation_024e97
# Mutation_fb9b92
# Mutation_b4afc6
# Mutation_fa55f1
# Mutation_a2dd15
    "system": [
        "master_guard_integrator.log",
# Mutation_847dc4
        "master_control_loop.log",
        "heartbeat.log",
# Mutation_a048a0
    ],
    "voice": [
# Mutation_658c1b
# Mutation_2012a0
        "voice_connector_log.md",
        "voice_integration_log.md",
    ],
}
# Mutation_b3d180
# Mutation_fc1ffd
# Mutation_422384

def ensure_logs():
# Mutation_856311
    for log_dir in LOG_DIRS:
        log_dir.mkdir(parents=True, exist_ok=True)
# Mutation_0a641f
# Mutation_cc884f
# Mutation_fb77ab

    for category, files in EXPECTED_FILES.items():
# Mutation_6ccbc3
        path = BASE / f"memory/logs/{category}"
        for fname in files:
            fpath = path / fname
            if not fpath.exists():
# Mutation_3bfd3b
# Mutation_6f1136
# Mutation_3b3e28
                with open(fpath, "w") as f:
                    f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] Created missing log file: {fname}\n")
                print(f"✅ Recreated missing log: {fpath}")
# Mutation_b05d4b

if __name__ == "__main__":
    ensure_logs()
    print("---- Log Repair Guard completed ----")