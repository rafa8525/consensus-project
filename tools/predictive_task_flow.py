#!/usr/bin/env python3
"""
predictive_task_flow.py
------------------------------------------------------------
Analyzes recent system reminder logs and timestamp patterns
to forecast upcoming tasks and activity windows.

Outputs:
  - predictive_task_flow.log   (human-readable summary)
  - predictive_task_flow.json  (structured JSON data)

Location:
  ~/memory/logs/system/predictive/
------------------------------------------------------------
"""

import os
import re
import json
import datetime
from collections import Counter

# === Paths ===
BASE_DIR   = os.path.expanduser("~/memory/logs/reminders")
OUT_DIR    = os.path.expanduser("~/memory/logs/system/predictive")
LOG_PATH   = os.path.join(OUT_DIR, "predictive_task_flow.log")
JSON_PATH  = os.path.join(OUT_DIR, "predictive_task_flow.json")

def timestamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def ensure_dirs():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

def read_recent_timestamps():
    """Read timestamps from reminder logs to find recurring task patterns."""
    timestamps = []
    if not os.path.exists(BASE_DIR):
        return timestamps

    for fname in os.listdir(BASE_DIR):
        if not fname.endswith(".log"):
            continue
        path = os.path.join(BASE_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    match = re.search(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                    if match:
                        try:
                            dt = datetime.datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
                            timestamps.append(dt)
                        except Exception:
                            pass
        except Exception:
            continue
    return timestamps

def analyze_timestamps(timestamps):
    """Determine peak hours and predict next likely task periods."""
    if not timestamps:
        return {"predicted_hours": [], "confidence": 0.0, "total": 0}

    hours = [t.hour for t in timestamps]
    counter = Counter(hours)
    total = sum(counter.values())
    top_hours = counter.most_common(3)
    avg_conf = round(min(0.95, 0.7 + (len(timestamps) / 1000.0)), 2)
    predicted = [h for h, _ in top_hours]

    return {
        "predicted_hours": predicted,
        "confidence": avg_conf,
        "total": total,
    }

def write_outputs(result):
    """Write both JSON and log summary outputs."""
    with open(JSON_PATH, "w", encoding="utf-8") as jf:
        json.dump(result, jf, indent=2)

    with open(LOG_PATH, "a", encoding="utf-8") as lf:
        lf.write(f"[{timestamp()}] Predicted hours: {result['predicted_hours']} | "
                 f"Confidence: {result['confidence']} | Based on {result['total']} entries\n")

def main():
    ensure_dirs()
    timestamps = read_recent_timestamps()
    result = analyze_timestamps(timestamps)
    write_outputs(result)
    print(f"[{timestamp()}] Predictive Task Flow complete — {len(result['predicted_hours'])} peak hour(s) predicted.")

if __name__ == "__main__":
    main()
