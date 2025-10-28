#!/usr/bin/env python3
"""
Progress Evaluation Runner
--------------------------
Evaluates all major subsystems weekly and lists corrective actions if deviations are found.
"""

import os
from datetime import datetime

BASE = "/home/rafa1215/consensus-project"
SYS_LOG = f"{BASE}/memory/logs/system/progress_evaluation.log"

CHECKS = {
    "VPN": f"{BASE}/memory/logs/system/vpn_test.log",
    "Security Audit": f"{BASE}/memory/logs/system/security_audit.log",
    "Weekly Report": f"{BASE}/memory/logs/system/weekly_status_report.txt",
    "Knowledge Sharing": f"{BASE}/memory/logs/system/knowledge_sharing_validation.log",
    "Fitness Verification": f"{BASE}/memory/logs/system/fitness_integration.log",
}

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(SYS_LOG), exist_ok=True)
    with open(SYS_LOG, "a") as f:
        f.write(line + "\n")

def check_file(path, label):
    if not os.path.exists(path):
        log(f"❌ {label}: Missing log file.")
        return False
    age_min = (datetime.now().timestamp() - os.path.getmtime(path)) / 60
    if age_min > 10080:  # 7 days
        log(f"⚠️ {label}: Last update >7 days ago ({age_min:.1f} min).")
        return False
    log(f"✅ {label}: Updated recently ({age_min:.1f} min ago).")
    return True

def corrective_action(label):
    actions = {
        "VPN": "Re-run vpn_auto_detect_activate.py and confirm cron active.",
        "Security Audit": "Trigger security_audit_runner.py manually; check for FAILs.",
        "Weekly Report": "Force weekly_status_report.py to rebuild report.",
        "Knowledge Sharing": "Run knowledge_sharing_validator.py to sync agents.",
        "Fitness Verification": "Ensure Fitbit/Pixel data sync; rerun fitness verifier.",
    }
    return actions.get(label, "Review subsystem manually.")

def main():
    log("---- Starting Weekly Progress Evaluation ----")
    failed = []
    for label, path in CHECKS.items():
        if not check_file(path, label):
            failed.append(label)

    if failed:
        log("⚠️ Deviations detected:")
        for f in failed:
            log(f"  → {corrective_action(f)}")
    else:
        log("✅ All subsystems up-to-date. No corrective action required.")
    log("---- Evaluation complete ----\n")

if __name__ == "__main__":
    main()
