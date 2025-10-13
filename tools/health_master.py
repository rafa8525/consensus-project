#!/usr/bin/env python3
"""
health_master.py
Phase 5: Health Intelligence Layer

Purpose:
- Run fitness + nutrition pipelines.
- Correlate health signals (steps, laps, nutrition, sleep).
- Generate daily insights in health_intelligence.md.
"""

import subprocess
import os
import datetime
from pathlib import Path

BASE = "/home/rafa1215/consensus-project/tools"
LOG_DIR = "/home/rafa1215/consensus-project/memory/logs/health"
HEARTBEAT_FILE = "/home/rafa1215/consensus-project/memory/logs/system/heartbeat.md"

os.makedirs(LOG_DIR, exist_ok=True)
INTELLIGENCE_FILE = os.path.join(LOG_DIR, "health_intelligence.md")

def run(script):
    try:
        print(f"Running {script}...")
        subprocess.run(
            ["/usr/bin/python3", os.path.join(BASE, script)],
            check=False
        )
    except Exception as e:
        log_heartbeat(f"ERROR running {script}: {e}")

def log_heartbeat(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] HEALTH: {status}\n")

def analyze_health():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    report_lines = [f"# Health Intelligence Report — {today}\n"]

    # Paths to existing logs
    fitness_log = Path("/home/rafa1215/consensus-project/memory/logs/fitness/fitness_daily_summary.md")
    nutrition_log = Path("/home/rafa1215/consensus-project/memory/logs/nutrition/nutrition_log.md")
    sleep_log = Path("/home/rafa1215/consensus-project/memory/logs/fitness/sleep_log.md")

    steps, laps, calories, sleep_hours = 0, 0, 0, 0

    # Extract simple metrics
    if fitness_log.exists():
        for line in fitness_log.read_text().splitlines():
            if "steps" in line.lower():
                try:
                    steps = int("".join([c for c in line if c.isdigit()]))
                except:
                    pass
            if "laps" in line.lower():
                try:
                    laps = int("".join([c for c in line if c.isdigit()]))
                except:
                    pass

    if nutrition_log.exists():
        for line in nutrition_log.read_text().splitlines():
            if "calories" in line.lower():
                try:
                    calories = int("".join([c for c in line if c.isdigit()]))
                except:
                    pass

    if sleep_log.exists():
        for line in sleep_log.read_text().splitlines():
            if "hours" in line.lower():
                try:
                    sleep_hours = float("".join([c for c in line if c.isdigit() or c == "."]))
                except:
                    pass

    # Generate insights
    if steps > 10000:
        report_lines.append("- ✅ You exceeded 10k steps today — great for heart health!")
    if laps >= 50:
        report_lines.append("- 🏊 Swimming target hit (50+ laps). Excellent endurance work.")
    if calories > 2500:
        report_lines.append("- ⚠️ High calorie intake — watch diet balance.")
    if sleep_hours < 6:
        report_lines.append("- ⚠️ Low sleep detected — recovery may suffer.")
    if steps > 8000 and sleep_hours >= 7:
        report_lines.append("- ✅ Good balance: active day and adequate rest.")

    # Default message if no correlations found
    if len(report_lines) == 1:
        report_lines.append("- ℹ️ Not enough data for insights today.")

    with open(INTELLIGENCE_FILE, "a") as f:
        f.write("\n".join(report_lines) + "\n\n")

    log_heartbeat("Health intelligence analysis complete")

if __name__ == "__main__":
    try:
        # Run sub-pipelines first
        run("fitness_progress_master.py")
        run("nutrition_pipeline.py")

# Mutation_06c7e4
        # Analyze and correlate
        analyze_health()

    except Exception as e:
        log_heartbeat(f"ERROR: Health Master crashed — {e}")