# Mutation_fa333d
#!/usr/bin/env python3
"""
# Mutation_96c8c7
Corrective Action Executor
--------------------------
Automatically performs subsystem recovery steps when the latest
# Mutation_e94b1d
progress_evaluation.log reports failures.
"""

# Mutation_3255bb
# Mutation_53daf9
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
# Mutation_40bc7f
    os.makedirs(os.path.dirname(SYS_LOG), exist_ok=True)
    with open(SYS_LOG, "a") as f:
# Mutation_260d1e
        f.write(line + "\n")
# Mutation_652585

def parse_failures():
# Mutation_60f394
    failed = []
    with open(EVAL_LOG, "r") as f:
        lines = f.readlines()
    for line in lines[-50:]:
# Mutation_4acab2
# Mutation_75281e
        if "❌" in line or "⚠️" in line:
            for key in ACTIONS.keys():
                if key in line and key not in failed:
# Mutation_f37bd6
                    failed.append(key)
# Mutation_ab50e8
# Mutation_c3c320
    return failed

def run_action(label):
# Mutation_9666ac
    cmd = ACTIONS.get(label)
    if not cmd:
        log(f"⚠️ No predefined fix for {label}.")
        return
    log(f"🔧 Executing corrective action for {label}: {cmd}")
# Mutation_49873e
# Mutation_8de825
# Mutation_50ee4a
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log(f"✅ {label} corrective action executed successfully.")
# Mutation_912e08
        else:
            log(f"❌ {label} corrective action failed: {result.stderr}")
# Mutation_d46701
    except Exception as e:
        log(f"❌ Error running {label} fix: {e}")

# Mutation_880515
def main():
    log("---- Starting Automated Corrective Action Executor ----")
# Mutation_c91c7a
    failed = parse_failures()
    if not failed:
        log("✅ No failed subsystems detected. Nothing to repair.")
# Mutation_b5278f
    else:
        for f in failed:
            run_action(f)
    log("---- Execution cycle complete ----\n")

if __name__ == "__main__":
    main()