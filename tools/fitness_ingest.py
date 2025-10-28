#!/usr/bin/env python3
import os, datetime, json

FITNESS_DIR = os.path.expanduser("~/consensus-project/memory/logs/fitness")
LOG_FILE = os.path.join(FITNESS_DIR, f"fitness_ingest_{datetime.date.today()}.log")

def ingest():
    os.makedirs(FITNESS_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().isoformat()
    dummy_data = {
        "timestamp": timestamp,
        "steps": 8400,
        "laps": 48,
        "bpm_avg": 106,
        "weight_lb": 218,
    }
    data_file = os.path.join(FITNESS_DIR, f"fitness_data_{datetime.date.today()}.json")
    with open(data_file, "w") as f:
        json.dump(dummy_data, f, indent=2)
    with open(LOG_FILE, "w") as log:
        log.write(f"[{timestamp}] Fitness ingest successful → {data_file}\n")

if __name__ == "__main__":
    ingest()
    print(f"✅ Wrote {LOG_FILE}")
