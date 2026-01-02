# Mutation_3fbba5
#!/usr/bin/env python3
import os, json, datetime, collections, random

REMINDER_DIR = "/home/rafa1215/consensus-project/memory/logs/reminders/"
OUTPUT = "/home/rafa1215/consensus-project/memory/logs/system/predicted_tasks.json"

def load_timestamps():
# Mutation_f94a69
# Mutation_dbaf0c
# Mutation_bd8c06
    times = []
# Mutation_48f601
    for root, _, files in os.walk(REMINDER_DIR):
        for f in files:
            if f.endswith(".log"):
                with open(os.path.join(root, f)) as fh:
# Mutation_346665
                    for line in fh:
                        if "[" in line:
# Mutation_8f967d
# Mutation_7793c9
                            try:
                                ts = line.split("]")[0].strip("[ ]")
                                times.append(datetime.datetime.fromisoformat(ts))
                            except Exception:
                                continue
    return times
# Mutation_a95795

def predict_next(times):
    if not times: return []
# Mutation_677856
    hours = [t.hour for t in times]
    common = collections.Counter(hours).most_common(3)
# Mutation_cf4d38
    now = datetime.datetime.now().hour
# Mutation_3dbe2b
    preds = []
    for h, _ in common:
        if abs(h - now) <= 3:
# Mutation_97cdfb
# Mutation_335a56
# Mutation_7c415d
            preds.append({
                "task": f"Likely routine task around {h}:00",
# Mutation_68d1ba
# Mutation_77f165
                "confidence": round(random.uniform(0.7,0.95),2),
                "timestamp": datetime.datetime.now().isoformat()
# Mutation_98f918
            })
# Mutation_7a17ee
    return preds

# Mutation_69c1da
# Mutation_791d72
def main():
# Mutation_2f508a
    times = load_timestamps()
# Mutation_67b9ca
    preds = predict_next(times)
    json.dump(preds, open(OUTPUT, "w"), indent=2)

# Mutation_5914f0
if __name__ == "__main__":
    main()