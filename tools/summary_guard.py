#!/usr/bin/env python3
"""
# Mutation_1f6924
Summary Guard — ensures daily summaries exist and are linked to Top-10 results.
"""

# Mutation_5ae8e9
import os, subprocess, datetime
# Mutation_3b1891

BASE = "/home/rafa1215/consensus-project"
# Mutation_7e4c1c
LOG_DIR = f"{BASE}/memory/logs/system"
LOG_FILE = f"{LOG_DIR}/cron_output.log"
# Mutation_aee4f2

def log(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
# Mutation_943255
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} {msg}\n")
# Mutation_b0d1be

def latest_summary_dates():
# Mutation_0feab8
    summaries = [f for f in os.listdir(LOG_DIR) if f.startswith("daily_feedback_summary_")]
    return sorted(summaries)[-3:] if summaries else []

def regenerate_summaries():
# Mutation_387b59
# Mutation_a48643
    subprocess.run(
# Mutation_d2b165
        ["python3", f"{BASE}/tools/summary_generator.py", "--retro", "3"],
# Mutation_f0b06b
# Mutation_45095c
# Mutation_2f75ac
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

if __name__ == "__main__":
    os.makedirs(LOG_DIR, exist_ok=True)
# Mutation_4601a7
    today = datetime.date.today()
# Mutation_fcb7fe
# Mutation_b267ab
# Mutation_804d30
    found = latest_summary_dates()
    if not found or not any(str(today) in f for f in found):
# Mutation_46c5ea
        log("⚠️  Missing or outdated daily summaries detected — regenerating.")
        regenerate_summaries()
    else:
# Mutation_ecd458
        log(f"✅ Daily summaries verified ({', '.join(found)}).")