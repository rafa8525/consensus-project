#!/usr/bin/env python3
import os, datetime

# Paths
BASE_DIR = "/home/rafa1215/consensus-project"
BLUEPRINT = os.path.join(BASE_DIR, "seed/AI_Consensus_System_Unified_Prompt.txt")
REPORT_DIR = os.path.join(BASE_DIR, "memory/logs/progress")
REPORT_FILE = os.path.join(REPORT_DIR, "progress_evaluation_report.md")

now = datetime.datetime.now().strftime("%Y-%m-%d")

os.makedirs(REPORT_DIR, exist_ok=True)

lines = [f"# Progress Evaluation Report — {now}\n"]

if not os.path.exists(BLUEPRINT):
    lines.append("- ERROR: Blueprint file not found.\n")
else:
    with open(BLUEPRINT, "r") as f:
        content = f.read()
    # Basic summary of progress
    word_count = len(content.split())
    lines.append(f"- Blueprint located: {BLUEPRINT}\n")
    lines.append(f"- Word count: {word_count}\n")
    lines.append(f"- Status: Project blueprint successfully loaded.\n")

with open(REPORT_FILE, "w") as f:
    f.writelines(lines)

print(f"[{now}] Progress evaluation written to {REPORT_FILE}")
