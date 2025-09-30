#!/usr/bin/env python3
import os
import datetime
import json
import random

BASE_DIR = "/home/rafa1215/consensus-project/memory"
FITNESS_DIR = os.path.join(BASE_DIR, "logs/fitness")
NUTRITION_DIR = os.path.join(BASE_DIR, "logs/nutrition")
REPORT_FILE = os.path.join(FITNESS_DIR, "fitness_daily_summary.md")
HEARTBEAT_FILE = os.path.join(BASE_DIR, "logs/system/heartbeat.md")

os.makedirs(FITNESS_DIR, exist_ok=True)
os.makedirs(NUTRITION_DIR, exist_ok=True)

# --- Heartbeat logger ---
def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] FITNESS: {status}\n")
    print(f"[HEARTBEAT] {status}")

# --- Device Sync (stubbed) ---
def sync_devices():
    devices = ["Fitbit", "Pixel Watch 3", "Samsung Watch", "COROS Pace 3"]
    synced = []
    for d in devices:
        synced.append({
            "device": d,
            "steps": random.randint(3000, 12000),
            "hr": random.randint(60, 140)
        })
    return synced

# --- Barcode Scanner Stub ---
def scan_barcode(upc: str):
    mock_db = {
        "755000000010": "Texas Pete Hot Sauce (Keto)",
        "73852145599": "Purell Sanitizer (Non-food)",
        "708747151930": "Power Up Trail Mix (Not Keto)"
    }
    return mock_db.get(upc, "Unknown Item")

# --- Geolocation Facility ---
def log_geofence(location: str, action: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = os.path.join(FITNESS_DIR, "geofence_log.md")
    with open(path, "a") as f:
        f.write(f"[{ts}] {action} at {location}\n")

# --- Push Notifications (stubbed) ---
def send_push(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = os.path.join(FITNESS_DIR, "push_log.md")
    with open(path, "a") as f:
        f.write(f"[{ts}] Notification: {msg}\n")

# --- Gamification ---
def update_streaks():
    streaks_file = os.path.join(FITNESS_DIR, "streaks.json")
    data = {"workout_streak": 0, "nutrition_streak": 0}
    if os.path.exists(streaks_file):
        with open(streaks_file, "r") as f:
            data = json.load(f)
    data["workout_streak"] += 1
    data["nutrition_streak"] += 1
    with open(streaks_file, "w") as f:
        json.dump(data, f)
    return data

# --- Daily Report ---
def generate_daily_report():
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        synced = sync_devices()
        streaks = update_streaks()
    except Exception as e:
        heartbeat_log(f"ERROR: Device sync or streak update failed — {e}")
        return None

    summary = [f"# Fitness Report {ts}\n"]
    summary.append("## Device Sync")
    for s in synced:
        summary.append(f"- {s['device']}: {s['steps']} steps, HR {s['hr']} bpm")

    summary.append("\n## Streaks")
    summary.append(f"- Workout Streak: {streaks['workout_streak']} days")
    summary.append(f"- Nutrition Streak: {streaks['nutrition_streak']} days")

    try:
        with open(REPORT_FILE, "w") as f:
            f.write("\n".join(summary))
    except Exception as e:
        heartbeat_log(f"ERROR: Could not write daily report — {e}")
        return None

    heartbeat_log("SUCCESS: Fitness daily report generated")
    return REPORT_FILE

if __name__ == "__main__":
    report = generate_daily_report()
    if report:
        log_geofence("Local Gym", "Workout Logged")
        log_geofence("Smith’s Landing", "Meal Logged")
        send_push("Time to log today’s workout!")
        send_push("Remember to scan your meal barcodes.")
        print(f"Daily fitness report generated: {report}")
