#!/usr/bin/env python3
import os
import time
from datetime import datetime

# --- NEW: Run memory folder bootstrap when voice mode starts ---
BOOTSTRAP_SCRIPT = "/home/rafa1215/consensus-project/memory/tools/voice_mode_bootstrap.py"
if os.path.exists(BOOTSTRAP_SCRIPT):
    os.system(f"python3 {BOOTSTRAP_SCRIPT}")

# Log file
LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/system/voice_reminder_watcher.log"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def main():
    log("Voice Reminder Watcher started.")
    
    while True:
        # Placeholder for actual voice trigger detection
        log("Listening for voice reminders...")
        # Example: poll or wait for event
        time.sleep(60)

if __name__ == "__main__":
    main()
