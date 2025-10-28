#!/usr/bin/env python3
"""
fitness_tracker.py
Purpose: Log basic health metrics and confirm system integration.
"""

import os
from datetime import datetime, timezone

LOG_DIR = "/home/rafa1215/consensus-project/memory/logs/fitness"
os.makedirs(LOG_DIR, exist_ok=True)

def run():
    """Write a timestamped fitness log entry."""
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = f"[fitness_tracker] Log entry at {timestamp}\n"
    log_file = os.path.join(LOG_DIR, "fitness_tracker.log")

    with open(log_file, "a") as f:
        f.write(entry)

    print(entry.strip())

if __name__ == "__main__":
    run()
