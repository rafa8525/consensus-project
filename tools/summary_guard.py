#!/usr/bin/env python3
"""
Summary Guard — ensures daily summaries exist and are linked to Top-10 results.
"""

import os, subprocess, datetime

BASE = "/home/rafa1215/consensus-project"
LOG_DIR = f"{BASE}/memory/logs/system"
LOG_FILE = f"{LOG_DIR}/cron_output.log"

def log(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} {msg}\n")

def latest_summary_dates():
    summaries = [f for f in os.listdir(LOG_DIR) if f.startswith("daily_feedback_summary_")]
    return sorted(summaries)[-3:] if summaries else []

def regenerate_summaries():
    subprocess.run(
        ["python3", f"{BASE}/tools/summary_generator.py", "--retro", "3"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

if __name__ == "__main__":
    os.makedirs(LOG_DIR, exist_ok=True)
    today = datetime.date.today()
    found = latest_summary_dates()
    if not found or not any(str(today) in f for f in found):
        log("⚠️  Missing or outdated daily summaries detected — regenerating.")
        regenerate_summaries()
    else:
        log(f"✅ Daily summaries verified ({', '.join(found)}).")
