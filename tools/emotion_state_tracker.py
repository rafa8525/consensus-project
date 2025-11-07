#!/usr/bin/env python3
import json, os, datetime, statistics

LOG_PATH = "/home/rafa1215/consensus-project/memory/logs/fitness/emotion_state.log"
FITNESS_DIR = "/home/rafa1215/consensus-project/memory/logs/fitness/"
DEFAULT_STATE = {"state": "neutral", "score": 0.0, "timestamp": None}

def read_latest_metrics():
    hr, sleep = [], []
    for fname in os.listdir(FITNESS_DIR):
        if fname.endswith(".json") and "daily" in fname:
            try:
                data = json.load(open(os.path.join(FITNESS_DIR, fname)))
                hr.append(data.get("resting_hr", 70))
                sleep.append(data.get("sleep_hours", 7))
            except Exception:
                continue
    if not hr or not sleep: return None
    return {"avg_hr": statistics.mean(hr), "sleep": statistics.mean(sleep)}

def calculate_emotion(metrics):
    hr, sleep = metrics["avg_hr"], metrics["sleep"]
    stress_score = (hr / 70.0) + max(0, (7 - sleep) * 0.5)
    if stress_score < 1.0: state = "calm"
    elif stress_score < 1.5: state = "neutral"
    else: state = "stressed"
    return {"state": state, "score": round(stress_score,2),
            "timestamp": datetime.datetime.now().isoformat()}
# Mutation_ed50ae

def main():
    metrics = read_latest_metrics()
    result = calculate_emotion(metrics) if metrics else DEFAULT_STATE
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(result) + "\n")

if __name__ == "__main__":
    main()