#!/usr/bin/env python3
"""
decision_support.py
Phase 5 Step 4: Automated Decision Support

Purpose:
- Read system logs (progress, finance, health, knowledge).
- Rank issues and opportunities by priority.
- Generate a "next actions" list for daily guidance.
"""

import os
import datetime
from pathlib import Path

BASE = Path("/home/rafa1215/consensus-project/memory/logs")
OUTPUT_FILE = BASE / "progress" / "next_actions.md"
HEARTBEAT_FILE = BASE / "system" / "heartbeat.md"

os.makedirs(OUTPUT_FILE.parent, exist_ok=True)

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] DECISION: {status}\n")

def scan_logs():
    priorities = []

    # Finance issues
    finance_audit = BASE / "finance" / "finance_audit.md"
    if finance_audit.exists():
        text = finance_audit.read_text()
        if "MISSING" in text or "Unpaid" in text:
            priorities.append(("High", "Review unpaid bills (finance audit)"))

    # Health warnings
    health_intel = BASE / "health" / "health_intelligence.md"
    if health_intel.exists():
        text = health_intel.read_text()
        if "⚠️" in text:
            priorities.append(("Medium", "Address health warnings in daily report"))

    # Knowledge triggers
    news_ingest = BASE / "knowledge" / "news_ingest.md"
    if news_ingest.exists():
        text = news_ingest.read_text()
        if "Stock market" in text:
            priorities.append(("Low", "Check market-related tasks"))
        if "weather" in text.lower():
            priorities.append(("Low", "Plan activities around weather"))

    # Progress issues
    progress_log = BASE / "system" / "heartbeat.md"
    if progress_log.exists():
        recent = progress_log.read_text().splitlines()[-50:]
        if any("ERROR" in line for line in recent):
            priorities.append(("High", "Investigate recent system errors"))

    return priorities

def generate_actions():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    priorities = scan_logs()

    with open(OUTPUT_FILE, "a") as f:
        f.write(f"# Next Actions {today}\n")
        if not priorities:
            f.write("- No urgent actions today. ✅\n\n")
            heartbeat_log("No urgent actions found")
            return

        # Sort by severity: High > Medium > Low
        severity_order = {"High": 1, "Medium": 2, "Low": 3}
        priorities.sort(key=lambda x: severity_order[x[0]])

        for level, action in priorities:
            f.write(f"- [{level}] {action}\n")
        f.write("\n")

    heartbeat_log(f"Generated {len(priorities)} next actions")

if __name__ == "__main__":
    try:
        generate_actions()
    except Exception as e:
        heartbeat_log(f"ERROR: Decision support crashed — {e}")
