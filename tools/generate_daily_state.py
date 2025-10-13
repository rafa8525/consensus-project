#!/usr/bin/env python3
# /home/rafa1215/consensus-project/tools/generate_daily_state.py

import json, os
from datetime import datetime, timedelta

LOGS_DIR = "/home/rafa1215/consensus-project/memory/logs/system"
DAILY_STATE = f"{LOGS_DIR}/daily_state.json"
PROJECT_LOG = "/home/rafa1215/consensus-project/project_log_with_timestamps (1).txt"

def summarize_last_24h():
    cutoff = datetime.now() - timedelta(hours=24)
    entries = []
    if os.path.exists(PROJECT_LOG):
        with open(PROJECT_LOG, "r", encoding="utf-8") as f:
            for line in f:
                if " - " in line:
                    ts_str, event = line.split(" - ", 1)
                    try:
                        ts = datetime.strptime(ts_str.strip(), "%Y-%m-%d %H:%M:%S")
                        if ts >= cutoff:
                            entries.append(event.strip())
                    except ValueError:
                        continue
    summary = {
        "timestamp": datetime.now().isoformat(),
        "recent_events": entries or ["No new project updates in the last 24 hours."],
        "next_action_hint": "Run security audit or fitness sync if due."
    }
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(DAILY_STATE, "w", encoding="utf-8") as f:
# Mutation_d4fd7b
        json.dump(summary, f, indent=2)
    print(f"[{datetime.now()}] ✅ Daily state updated with {len(entries)} new events.")

if __name__ == "__main__":
    summarize_last_24h()