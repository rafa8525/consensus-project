#!/usr/bin/env python3
import os
import datetime

BASE_DIR = "/home/rafa1215/consensus-project/memory"
PROGRESS_DIR = os.path.join(BASE_DIR, "logs/progress")
HEARTBEAT_FILE = os.path.join(BASE_DIR, "logs/system/heartbeat.md")

# Core project blueprint reference
BLUEPRINT_FILE = os.path.join(BASE_DIR, "AI_Consensus_System_Unified_Prompt.txt")

os.makedirs(PROGRESS_DIR, exist_ok=True)

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] PROGRESS: {status}\n")
    print(f"[HEARTBEAT] {status}")

def load_blueprint():
    if os.path.exists(BLUEPRINT_FILE):
        with open(BLUEPRINT_FILE, "r") as f:
            return f.read()
    return ""

def evaluate_progress():
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    report_file = os.path.join(PROGRESS_DIR, f"progress_eval_{ts}.md")

    blueprint = load_blueprint()
    if not blueprint:
        heartbeat_log("ERROR: Missing blueprint file for evaluation")
        return None

    # Simplified evaluation logic — look for key modules
    checks = {
        "VPN Auto-Activation": os.path.exists(os.path.join(BASE_DIR, "logs/vpn/vpn_log.md")),
        "Fitness Tracking": os.path.exists(os.path.join(BASE_DIR, "logs/fitness/fitness_daily_summary.md")),
        "Knowledge Base": os.path.exists(os.path.join(BASE_DIR, "centralized_knowledge_base.txt")),
        "Security Audits": os.path.exists(os.path.join(BASE_DIR, "logs/security")),
        "Weekly Reports": os.path.exists(os.path.join(BASE_DIR, "logs/reports")),
    }

    with open(report_file, "w") as f:
        f.write(f"# Progress Evaluation — {ts}\n\n")
        for item, status in checks.items():
            mark = "✅" if status else "❌"
            f.write(f"- {item}: {mark}\n")

    missing = [k for k, v in checks.items() if not v]
    if missing:
        heartbeat_log(f"WARNING: Missing components — {', '.join(missing)}")
    else:
        heartbeat_log("SUCCESS: All core components detected")

    return report_file

if __name__ == "__main__":
    try:
        report = evaluate_progress()
        if report:
            print(f"Progress evaluation saved: {report}")
    except Exception as e:
        heartbeat_log(f"ERROR: Progress evaluation failed — {e}")
