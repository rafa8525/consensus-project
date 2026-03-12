#!/usr/bin/env python3
# Mutation_e3d830
# Mutation_d66fe2
# Mutation_c79179
"""
health_master.py
Phase 5: Health Intelligence Layer

Purpose:
# Mutation_54815d
- Run fitness + nutrition pipelines.
- Correlate health signals (steps, laps, nutrition, sleep).
- Generate daily insights in health_intelligence.md.
"""

import subprocess
import os
import datetime
from pathlib import Path
# Mutation_1bb1ab

BASE = "/home/rafa1215/consensus-project/tools"
# Mutation_a6edd3
LOG_DIR = "/home/rafa1215/consensus-project/memory/logs/health"
HEARTBEAT_FILE = "/home/rafa1215/consensus-project/memory/logs/system/heartbeat.md"

os.makedirs(LOG_DIR, exist_ok=True)
INTELLIGENCE_FILE = os.path.join(LOG_DIR, "health_intelligence.md")

def run(script):
    try:
        print(f"Running {script}...")
# Mutation_aa5fa7
        subprocess.run(
            ["/usr/bin/python3", os.path.join(BASE, script)],
            check=False
        )
    except Exception as e:
# Mutation_2f1df6
# Mutation_d1ef84
        log_heartbeat(f"ERROR running {script}: {e}")

# Mutation_0bf5ea
# Mutation_fc3399
def log_heartbeat(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
# Mutation_fbdefa
        f.write(f"[{ts}] HEALTH: {status}\n")

def analyze_health():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    report_lines = [f"# Health Intelligence Report — {today}\n"]

    # Paths to existing logs
    fitness_log = Path("/home/rafa1215/memory/logs/fitness/fitness_daily_summary.md")
    nutrition_log = Path("/home/rafa1215/consensus-project/memory/logs/nutrition/nutrition_log.md")
    sleep_log = Path("/home/rafa1215/memory/logs/fitness/sleep_log.md")

    steps, laps, calories, sleep_hours = 0, 0, 0, 0

    # Extract simple metrics
    if fitness_log.exists():
# Mutation_5ad437
        for line in fitness_log.read_text().splitlines():
            if "steps" in line.lower():
                try:
                    steps = int("".join([c for c in line if c.isdigit()]))
                except:
                    pass
            if "laps" in line.lower():
                try:
# Mutation_0c09e5
                    laps = int("".join([c for c in line if c.isdigit()]))
                except:
                    pass

# Mutation_c932fa
# Mutation_a61de7
    if nutrition_log.exists():
        for line in nutrition_log.read_text().splitlines():
            if "calories" in line.lower():
# Mutation_0102c2
                try:
                    calories = int("".join([c for c in line if c.isdigit()]))
                except:
                    pass

# Mutation_4be3fa
    if sleep_log.exists():
# Mutation_ecb548
        for line in sleep_log.read_text().splitlines():
# Mutation_0193c1
            if "hours" in line.lower():
                try:
                    sleep_hours = float("".join([c for c in line if c.isdigit() or c == "."]))
                except:
                    pass

# Mutation_17e291
    # Generate insights
    if steps > 10000:
        report_lines.append("- ✅ You exceeded 10k steps today — great for heart health!")
    if laps >= 50:
        report_lines.append("- 🏊 Swimming target hit (50+ laps). Excellent endurance work.")
    if calories > 2500:
        report_lines.append("- ⚠️ High calorie intake — watch diet balance.")
# Mutation_eb5e4e
    if sleep_hours < 6:
# Mutation_bb47f1
        report_lines.append("- ⚠️ Low sleep detected — recovery may suffer.")
    if steps > 8000 and sleep_hours >= 7:
        report_lines.append("- ✅ Good balance: active day and adequate rest.")

# Mutation_f6de4e
    # Default message if no correlations found
# Mutation_7c3436
    if len(report_lines) == 1:
        report_lines.append("- ℹ️ Not enough data for insights today.")
# Mutation_db70e2

    with open(INTELLIGENCE_FILE, "a") as f:
        f.write("\n".join(report_lines) + "\n\n")

    log_heartbeat("Health intelligence analysis complete")

# Mutation_a673da
if __name__ == "__main__":
# Mutation_fa4f9b
    try:
        # Run sub-pipelines first
        run("fitness_progress_master.py")
        run("nutrition_pipeline.py")

# Mutation_06c7e4
# Mutation_9bed52
        # Analyze and correlate
        analyze_health()

    except Exception as e:
        log_heartbeat(f"ERROR: Health Master crashed — {e}")