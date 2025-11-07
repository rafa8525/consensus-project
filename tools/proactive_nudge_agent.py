#!/usr/bin/env python3
from datetime import datetime, timedelta

LOG_PATH = "/home/rafa1215/memory/logs/status/proactive_nudge_agent.log"

def log(msg):
    with open(LOG_PATH, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def generate_nudges():
    reminders = [
        ("Security Audit", datetime.now() + timedelta(days=28)),
        ("Fitness Log", datetime.now() + timedelta(hours=12)),
    ]
    for name, time_due in reminders:
        log(f"Nudge generated → {name} scheduled for {time_due.strftime('%Y-%m-%d %H:%M PST')}")

if __name__ == "__main__":
    log("=== Proactive Nudge Agent Run ===")
    generate_nudges()
    log("✅ All nudges recorded\n")
