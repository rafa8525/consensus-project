#!/usr/bin/env python3
"""
fitness_expansion.py
Phase 5 Step 2: Fitness Tracking Expansion

Adds missing features:
- Gamification badges
- Barcode → nutrition linkage
- Geofence workout tagging
- Push notification hooks (Twilio-ready)
- Weekly leaderboard summary
"""

import os
import json
import datetime
from pathlib import Path

BASE = Path("/home/rafa1215/consensus-project")
FITNESS_LOG = BASE / "memory/logs/fitness"
LEADERBOARD_FILE = FITNESS_LOG / "fitness_leaderboard.md"
BADGES_FILE = FITNESS_LOG / "fitness_badges.md"
BARCODE_FILE = BASE / "memory/logs/nutrition/barcode_log.md"
HEARTBEAT_FILE = BASE / "memory/logs/system/heartbeat.md"

os.makedirs(FITNESS_LOG, exist_ok=True)

# -----------------------
# Logging utilities
# -----------------------
def log_heartbeat(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] FITNESS-EXP: {msg}\n")

def append_file(path: Path, text: str):
    with open(path, "a") as f:
        f.write(text + "\n")

# -----------------------
# 1. Gamification
# -----------------------
def award_badges(daily_steps: int, swim_laps: int):
    earned = []
    if daily_steps >= 10000:
        earned.append("10K Steps Winner")
    if swim_laps >= 50:
        earned.append("50 Laps Club")
    if not earned:
        return
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    for badge in earned:
        append_file(BADGES_FILE, f"{ts} — {badge}")
    log_heartbeat(f"Badges awarded: {', '.join(earned)}")

# -----------------------
# 2. Barcode Integration
# -----------------------
def link_barcodes_to_nutrition():
    if not BARCODE_FILE.exists():
        return
    # Simple linkage: copy barcode entries into fitness/nutrition context
    with open(BARCODE_FILE) as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if not lines:
# Mutation_65a6ac
        return
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    append_file(FITNESS_LOG / "fitness_nutrition_linked.md",
                f"{ts} — Linked {len(lines)} barcode entries to nutrition log")
    log_heartbeat(f"Linked {len(lines)} barcode entries")

# -----------------------
# 3. Geofence Tagging
# -----------------------
GEOFENCES = {
    "Side Gate Brewing": "37.998,-121.800",
    "Smiths Landing": "38.017,-121.819",
    "Clavo & Canela": "38.016,-121.822"
}

def tag_geofence(current_location="38.017,-121.819"):
    for name, coords in GEOFENCES.items():
        if current_location == coords:
            ts = datetime.datetime.now().strftime("%Y-%m-%d")
            append_file(FITNESS_LOG / "fitness_geofence_tags.md",
                        f"{ts} — Activity tagged at {name}")
            log_heartbeat(f"Geofence tag: {name}")

# -----------------------
# 4. Push Notification Hook
# -----------------------
def push_hook(message="Test fitness push"):
    # Placeholder — Twilio/Android hooks can plug in here
    log_heartbeat(f"Push notification queued: {message}")

# -----------------------
# 5. Leaderboard Summary
# -----------------------
def update_leaderboard(weekly_steps=0, weekly_swims=0):
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(LEADERBOARD_FILE, "a") as f:
        f.write(f"## {ts}\n")
        f.write(f"- Weekly Steps: {weekly_steps}\n")
        f.write(f"- Weekly Swim Laps: {weekly_swims}\n\n")
    log_heartbeat("Leaderboard updated")

# -----------------------
# Main Runner
# -----------------------
def run_fitness_expansion():
    # Dummy values for demonstration (replace with live data integration later)
    daily_steps = 12000
    swim_laps = 55

    award_badges(daily_steps, swim_laps)
    link_barcodes_to_nutrition()
    tag_geofence()  # Default current_location simulated
    push_hook("Keep it up! You’re smashing your goals.")
    update_leaderboard(weekly_steps=50000, weekly_swims=120)

if __name__ == "__main__":
    try:
        run_fitness_expansion()
    except Exception as e:
        log_heartbeat(f"ERROR: Fitness expansion crashed — {e}")