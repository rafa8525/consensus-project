#!/usr/bin/env python3
import os
from datetime import datetime

LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/system/voice_mode_bootstrap.log"
SCAN_SCRIPT = "/home/rafa1215/consensus-project/memory/tools/memory_folder_heartbeat.py"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def run_memory_scan():
    log("Voice mode opened → running memory folder deep scan...")
    os.system(f"python3 {SCAN_SCRIPT}")
    log("Memory folder scan complete for voice mode bootstrap.")

if __name__ == "__main__":
    run_memory_scan()
