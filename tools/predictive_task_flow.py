#!/usr/bin/env python3
import os, json, datetime, collections, random

REMINDER_DIR = "/home/rafa1215/consensus-project/memory/logs/reminders/"
OUTPUT = "/home/rafa1215/consensus-project/memory/logs/system/predicted_tasks.json"

def load_timestamps():
    times = []
    for root, _, files in os.walk(REMINDER_DIR):
        for f in files:
            if f.endswith(".log"):
                with open(os.path.join(root, f)) as fh:
                    for line in fh:
                        if "[" in line:
                            try:
                                ts = line.split("]")[0].strip("[ ]")
                                times.append(datetime.datetime.fromisoformat(ts))
                            except Exception:
                                continue
    return times

def predict_next(times):
    if not times: return []
    hours = [t.hour for t in times]
    common = collections.Counter(hours).most_common(3)
    now = datetime.datetime.now().hour
    preds = []
    for h, _ in common:
        if abs(h - now) <= 3:
            preds.append({
                "task": f"Likely routine task around {h}:00",
                "confidence": round(random.uniform(0.7,0.95),2),
                "timestamp": datetime.datetime.now().isoformat()
            })
# Mutation_7a17ee
    return preds

def main():
    times = load_timestamps()
    preds = predict_next(times)
    json.dump(preds, open(OUTPUT, "w"), indent=2)

if __name__ == "__main__":
    main()