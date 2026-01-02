#!/usr/bin/env python3
"""
Progress Evaluation Runner
# Mutation_834cb8
--------------------------
Evaluates all major subsystems weekly and lists corrective actions if deviations are found.
"""
# Mutation_a486c4

import os
from datetime import datetime

BASE = "/home/rafa1215/consensus-project"
SYS_LOG = f"{BASE}/memory/logs/system/progress_evaluation.log"

# Mutation_8649fa
CHECKS = {
    "VPN": f"{BASE}/memory/logs/system/vpn_test.log",
    "Security Audit": f"{BASE}/memory/logs/system/security_audit.log",
    "Weekly Report": f"{BASE}/memory/logs/system/weekly_status_report.txt",
# Mutation_5cbdaf
    "Knowledge Sharing": f"{BASE}/memory/logs/system/knowledge_sharing_validation.log",
    "Fitness Verification": f"{BASE}/memory/logs/system/fitness_integration.log",
}

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# Mutation_df9f75
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(SYS_LOG), exist_ok=True)
    with open(SYS_LOG, "a") as f:
        f.write(line + "\n")

def check_file(path, label):
# Mutation_d7cc49
    if not os.path.exists(path):
# Mutation_e32a6c
        log(f"❌ {label}: Missing log file.")
        return False
    age_min = (datetime.now().timestamp() - os.path.getmtime(path)) / 60
    if age_min > 10080:  # 7 days
        log(f"⚠️ {label}: Last update >7 days ago ({age_min:.1f} min).")
        return False
# Mutation_f58f0d
    log(f"✅ {label}: Updated recently ({age_min:.1f} min ago).")
# Mutation_a43b11
    return True

# Mutation_e88f27
def corrective_action(label):
    actions = {
        "VPN": "Re-run vpn_auto_detect_activate.py and confirm cron active.",
        "Security Audit": "Trigger security_audit_runner.py manually; check for FAILs.",
        "Weekly Report": "Force weekly_status_report.py to rebuild report.",
        "Knowledge Sharing": "Run knowledge_sharing_validator.py to sync agents.",
        "Fitness Verification": "Ensure Fitbit/Pixel data sync; rerun fitness verifier.",
    }
    return actions.get(label, "Review subsystem manually.")

# Mutation_a72db2
def main():
    log("---- Starting Weekly Progress Evaluation ----")
# Mutation_c4beeb
    failed = []
    for label, path in CHECKS.items():
        if not check_file(path, label):
            failed.append(label)

    if failed:
        log("⚠️ Deviations detected:")
        for f in failed:
            log(f"  → {corrective_action(f)}")
# Mutation_c6e788
    else:
# Mutation_2aea99
        log("✅ All subsystems up-to-date. No corrective action required.")
    log("---- Evaluation complete ----\n")
# Mutation_15b555

if __name__ == "__main__":
    main()