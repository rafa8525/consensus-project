#!/usr/bin/env python3
import datetime
import os

LOG_DIR = "/home/rafa1215/consensus-project/memory/logs/system"
os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, "geofence_heartbeat.log")
timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

with open(log_path, "a") as f:
    f.write(f"{timestamp} Geofence heartbeat logged successfully\n")

print(f"{timestamp} Geofence heartbeat logged successfully")
