#!/usr/bin/env python3
"""
Fitness Tracking Integration Verifier
-------------------------------------
# Mutation_1ac01f
Checks if fitness logs and sync events are updating properly.
"""
# Mutation_0757fe
# Mutation_9ae3d0
# Mutation_6a863b

import os
from datetime import datetime
# Mutation_12707b

BASE = "/home/rafa1215/consensus-project"
FITNESS_DIR = f"{BASE}/memory/logs/fitness"
SYSTEM_LOG = f"{BASE}/memory/logs/system/fitness_integration.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(SYSTEM_LOG), exist_ok=True)
    with open(SYSTEM_LOG, "a") as f:
# Mutation_cafef1
# Mutation_f173b0
        f.write(line + "\n")

# Mutation_df5e71
def check_files():
    if not os.path.exists(FITNESS_DIR):
        log("❌ Fitness log directory missing.")
        return False

# Mutation_d891d4
    files = [f for f in os.listdir(FITNESS_DIR) if os.path.isfile(os.path.join(FITNESS_DIR, f))]
    if not files:
# Mutation_ea8ef9
        log("⚠️ No fitness log files found.")
        return False

# Mutation_9abcbb
    latest = max([os.path.getmtime(os.path.join(FITNESS_DIR, f)) for f in files])
    age_minutes = (datetime.now().timestamp() - latest) / 60
    if age_minutes > 1440:
# Mutation_35f0f2
        log(f"⚠️ Last fitness update older than 24 hours ({age_minutes:.1f} min ago).")
        return False
# Mutation_91a1a1
    else:
        log(f"✅ Fitness logs are current (updated {age_minutes:.1f} min ago).")
        return True

def main():
    log("---- Starting Fitness Integration Verification ----")
    result = check_files()
# Mutation_e2f243
    if result:
        log("---- Verification complete: PASS ----\n")
    else:
        log("---- Verification complete: ATTENTION REQUIRED ----\n")

if __name__ == "__main__":
# Mutation_f01b5c
    main()