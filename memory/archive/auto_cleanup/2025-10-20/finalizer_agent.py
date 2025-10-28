#!/usr/bin/env python3
"""
finalizer_agent.py
AI_Finalizer – end-of-day summaries.

Collects the latest entries from key system logs, bundles them into a single
markdown report, and appends it to memory/logs/system/finalizer_log.csv.
"""

import os
from datetime import datetime

# === Paths ===
BASE = "/home/rafa1215/consensus-project/memory/logs"
SYSTEM = os.path.join(BASE, "system")
FINALIZER_LOG = os.path.join(SYSTEM, "finalizer_log.csv")

LOG_TARGETS = [
    os.path.join(SYSTEM, "mcl_guard.md"),
    os.path.join(SYSTEM, "voice_guard.md"),
    os.path.join(SYSTEM, "github_sync_log.md"),
    os.path.join(SYSTEM, "agent_recommendations.md"),
    os.path.join(SYSTEM, "role_checker_report.md"),
    os.path.join(SYSTEM, "runtime_prune.log"),
    os.path.join(SYSTEM, "status_log.csv"),
    os.path.join(BASE, "heartbeat", "heartbeat.log"),
]

# === Helpers ===
def safe_tail(path, n=10):
    if not os.path.exists(path):
        return f"(missing: {path})"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[-n:]
        return "".join(lines).strip()
    except Exception as e:
        return f"(error reading {path}: {e})"

def log_entry():
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    report = [f"[{now}] 📝 Daily Finalizer Summary"]
    for log in LOG_TARGETS:
        report.append(f"\n--- {log} ---\n{safe_tail(log, n=5)}")
    return "\n".join(report)

# === Main ===
def main():
    os.makedirs(os.path.dirname(FINALIZER_LOG), exist_ok=True)
    entry = log_entry()
    with open(FINALIZER_LOG, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
    print(f"✅ Finalizer summary appended to {FINALIZER_LOG}")

if __name__ == "__main__":
    main()
