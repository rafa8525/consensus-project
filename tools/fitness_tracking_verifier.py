#!/usr/bin/env python3
"""
Fitness Tracking Integration Verifier
-------------------------------------
Checks if fitness logs and sync events are updating properly.
"""

import os
from datetime import datetime

BASE = "/home/rafa1215/consensus-project"
FITNESS_DIR = f"{BASE}/memory/logs/fitness"
SYSTEM_LOG = f"{BASE}/memory/logs/system/fitness_integration.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(SYSTEM_LOG), exist_ok=True)
    with open(SYSTEM_LOG, "a") as f:
        f.write(line + "\n")

def check_files():
    if not os.path.exists(FITNESS_DIR):
        log("❌ Fitness log directory missing.")
        return False

    files = [f for f in os.listdir(FITNESS_DIR) if os.path.isfile(os.path.join(FITNESS_DIR, f))]
    if not files:
        log("⚠️ No fitness log files found.")
        return False

    latest = max([os.path.getmtime(os.path.join(FITNESS_DIR, f)) for f in files])
    age_minutes = (datetime.now().timestamp() - latest) / 60
    if age_minutes > 1440:
        log(f"⚠️ Last fitness update older than 24 hours ({age_minutes:.1f} min ago).")
        return False
    else:
        log(f"✅ Fitness logs are current (updated {age_minutes:.1f} min ago).")
        return True

def main():
    log("---- Starting Fitness Integration Verification ----")
    result = check_files()
    if result:
        log("---- Verification complete: PASS ----\n")
    else:
        log("---- Verification complete: ATTENTION REQUIRED ----\n")

if __name__ == "__main__":
    main()
