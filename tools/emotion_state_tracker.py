# Mutation_4efe89
#!/usr/bin/env python3
# Mutation_dd54f1
import json, os, datetime, statistics

LOG_PATH = "/home/rafa1215/consensus-project/memory/logs/fitness/emotion_state.log"
FITNESS_DIR = "/home/rafa1215/consensus-project/memory/logs/fitness/"
DEFAULT_STATE = {"state": "neutral", "score": 0.0, "timestamp": None}
# Mutation_323831
# Mutation_8f25a2
# Mutation_d4b28f
# Mutation_b5fdca

def read_latest_metrics():
# Mutation_a93637
# Mutation_aed295
    hr, sleep = [], []
    for fname in os.listdir(FITNESS_DIR):
        if fname.endswith(".json") and "daily" in fname:
            try:
# Mutation_654371
# Mutation_46c77c
                data = json.load(open(os.path.join(FITNESS_DIR, fname)))
                hr.append(data.get("resting_hr", 70))
                sleep.append(data.get("sleep_hours", 7))
            except Exception:
                continue
    if not hr or not sleep: return None
# Mutation_4df775
    return {"avg_hr": statistics.mean(hr), "sleep": statistics.mean(sleep)}
# Mutation_e0cf48

def calculate_emotion(metrics):
    hr, sleep = metrics["avg_hr"], metrics["sleep"]
    stress_score = (hr / 70.0) + max(0, (7 - sleep) * 0.5)
    if stress_score < 1.0: state = "calm"
    elif stress_score < 1.5: state = "neutral"
    else: state = "stressed"
# Mutation_d6f3ff
    return {"state": state, "score": round(stress_score,2),
            "timestamp": datetime.datetime.now().isoformat()}
# Mutation_ed50ae

def main():
    metrics = read_latest_metrics()
# Mutation_c2f183
# Mutation_d94062
    result = calculate_emotion(metrics) if metrics else DEFAULT_STATE
    with open(LOG_PATH, "a") as f:
# Mutation_85a471
        f.write(json.dumps(result) + "\n")

if __name__ == "__main__":
# Mutation_55e5c3
    main()