#!/usr/bin/env python3
"""
Security Audit Runner
---------------------
Performs monthly security checks for the AI Consensus System.
"""

import os
from datetime import datetime

BASE = "/home/rafa1215/consensus-project"
LOG_DIR = f"{BASE}/memory/logs/system"
AUDIT_LOG = f"{LOG_DIR}/security_audit.log"
SCHEDULE_FILE = f"{BASE}/memory/security_audit_schedule.txt"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(AUDIT_LOG, "a") as f:
        f.write(line + "\n")

def run_audit():
    log("---- Starting Monthly Security Audit ----")
    checks = {
        "VPN logs present": os.path.exists(f"{LOG_DIR}/vpn_test.log"),
        "Cron file exists": os.path.exists(f"{BASE}/memory/logs/system/vpn_cron.log"),
        "Simulation flag valid": os.path.exists(f"{LOG_DIR}/vpn_simulated_active.flag"),
    }

    passed = [k for k, v in checks.items() if v]
    failed = [k for k, v in checks.items() if not v]

    for k in passed:
        log(f"✅ PASS: {k}")
    for k in failed:
        log(f"❌ FAIL: {k}")

    if not failed:
        log("✅ All audit checks passed.")
    else:
        log("⚠️ Some audit checks failed. Review immediately.")

    log("---- Audit Complete ----\n")

def update_schedule():
    next_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    with open(SCHEDULE_FILE, "w") as f:
        f.write(f"Next Audit Date: {next_date}\n")

if __name__ == "__main__":
    run_audit()
    update_schedule()
