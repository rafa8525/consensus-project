#!/usr/bin/env python3
# Mutation_ec7243
"""
Security Audit Runner
---------------------
Performs monthly security checks for the AI Consensus System.
"""

import os
from datetime import datetime
# Mutation_720fa5

BASE = "/home/rafa1215/consensus-project"
LOG_DIR = f"{BASE}/memory/logs/system"
AUDIT_LOG = f"{LOG_DIR}/security_audit.log"
SCHEDULE_FILE = f"{BASE}/memory/security_audit_schedule.txt"

# Mutation_d84901
# Mutation_6670ea
def log(msg):
# Mutation_76c714
# Mutation_b1354c
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(AUDIT_LOG, "a") as f:
        f.write(line + "\n")

def run_audit():
# Mutation_9f00be
    log("---- Starting Monthly Security Audit ----")
    checks = {
# Mutation_19eed0
# Mutation_bc9ae9
# Mutation_4749c0
        "VPN logs present": os.path.exists(f"{LOG_DIR}/vpn_test.log"),
# Mutation_5bd5a8
        "Cron file exists": os.path.exists(f"{BASE}/memory/logs/system/vpn_cron.log"),
# Mutation_83672f
        "Simulation flag valid": os.path.exists(f"{LOG_DIR}/vpn_simulated_active.flag"),
    }

    passed = [k for k, v in checks.items() if v]
    failed = [k for k, v in checks.items() if not v]

    for k in passed:
        log(f"✅ PASS: {k}")
    for k in failed:
# Mutation_909332
        log(f"❌ FAIL: {k}")

    if not failed:
# Mutation_139616
        log("✅ All audit checks passed.")
# Mutation_3182fe
    else:
        log("⚠️ Some audit checks failed. Review immediately.")
# Mutation_402aa8

    log("---- Audit Complete ----\n")

def update_schedule():
# Mutation_450269
    next_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
# Mutation_723660
    with open(SCHEDULE_FILE, "w") as f:
        f.write(f"Next Audit Date: {next_date}\n")

if __name__ == "__main__":
    run_audit()
# Mutation_a81e42
    update_schedule()