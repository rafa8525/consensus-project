#!/usr/bin/env python3
"""
Corrective Action Executor
--------------------------
Automatically performs subsystem recovery steps when the latest
progress_evaluation.log reports failures.
"""

import os
from datetime import datetime
import subprocess

BASE = "/home/rafa1215/consensus-project"
SYS_LOG = f"{BASE}/memory/logs/system/corrective_action.log"
EVAL_LOG = f"{BASE}/memory/logs/system/progress_evaluation.log"

ACTIONS = {
    "VPN": f"/usr/bin/python3 {BASE}/tools/vpn_auto_detect_activate.py",
    "Security Audit": f"/usr/bin/python3 {BASE}/tools/security_audit_runner.py",
    "Weekly Report": f"/usr/bin/python3 {BASE}/tools/weekly_status_report.py",
    "Knowledge Sharing": f"/usr/bin/python3 {BASE}/tools/knowledge_sharing_validator.py",
    "Fitness Verification": f"/usr/bin/python3 {BASE}/tools/fitness_tracking_verifier.py",
}

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(SYS_LOG), exist_ok=True)
    with open(SYS_LOG, "a") as f:
        f.write(line + "\n")

def parse_failures():
    failed = []
    with open(EVAL_LOG, "r") as f:
        lines = f.readlines()
    for line in lines[-50:]:
        if "❌" in line or "⚠️" in line:
            for key in ACTIONS.keys():
                if key in line and key not in failed:
                    failed.append(key)
    return failed

def run_action(label):
    cmd = ACTIONS.get(label)
    if not cmd:
        log(f"⚠️ No predefined fix for {label}.")
        return
    log(f"🔧 Executing corrective action for {label}: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log(f"✅ {label} corrective action executed successfully.")
        else:
            log(f"❌ {label} corrective action failed: {result.stderr}")
    except Exception as e:
        log(f"❌ Error running {label} fix: {e}")

def main():
    log("---- Starting Automated Corrective Action Executor ----")
    failed = parse_failures()
    if not failed:
        log("✅ No failed subsystems detected. Nothing to repair.")
    else:
        for f in failed:
            run_action(f)
    log("---- Execution cycle complete ----\n")

if __name__ == "__main__":
    main()
