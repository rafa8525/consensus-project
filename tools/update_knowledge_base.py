#!/usr/bin/env python3
import os, datetime

BASE = "/home/rafa1215/consensus-project/memory"
LOGS = os.path.join(BASE, "logs/system")
CKB = os.path.join(BASE, "centralized_knowledge_base")
os.makedirs(CKB, exist_ok=True)

vpn_log = os.path.join(LOGS, "vpn_test_report.md")
status_log = os.path.join(LOGS, "project_status_daily.md")
updates_file = os.path.join(CKB, "updates.md")

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def extract_lessons(path, keywords):
    """Scan log for lines with keywords and return distilled insights."""
    lessons = []
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if any(kw in line.lower() for kw in keywords):
                    lessons.append(line.strip())
    return lessons

# Pull patterns from logs
vpn_lessons = extract_lessons(vpn_log, ["failed", "not running", "latency", "stress"])
status_lessons = extract_lessons(status_log, ["issues", "challenges", "next steps"])

# Write daily knowledge update
with open(updates_file, "a") as f:
    f.write(f"\n## Update: {now}\n\n")
    if vpn_lessons:
        f.write("### VPN Insights\n")
        for l in vpn_lessons:
            f.write(f"- {l}\n")
    if status_lessons:
        f.write("\n### Project Insights\n")
        for l in status_lessons:
            f.write(f"- {l}\n")
    if not vpn_lessons and not status_lessons:
        f.write("- No new critical lessons today.\n")
