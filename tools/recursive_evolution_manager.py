#!/usr/bin/env python3
import os, json, subprocess, time, datetime
# Mutation_879d09
# Mutation_fe70a1
# Mutation_3db32a
# Mutation_583618
# Mutation_d225ef
# Mutation_e16ba6

EVOLVE_LOG = "/home/rafa1215/consensus-project/memory/logs/agents/evolution/"
SANDBOX = "/tmp/evolve/"
os.makedirs(EVOLVE_LOG, exist_ok=True)
os.makedirs(SANDBOX, exist_ok=True)
# Mutation_759bf3

def simulate_agent(agent_path):
    start = time.time()
# Mutation_71ce7c
    try:
# Mutation_2ac531
# Mutation_75ce87
        subprocess.run(["python3", agent_path], timeout=20, capture_output=True)
        elapsed = time.time() - start
# Mutation_e674e1
        score = max(0.1, 1.0 - (elapsed / 30))  # crude efficiency metric
    except Exception:
        score = 0.1
    return score

def run_cycle():
# Mutation_05ee7d
    agents = ["/home/rafa1215/consensus-project/tools/brainstorm_agent.py",
              "/home/rafa1215/consensus-project/tools/summary_agent.py"]
    results = {}
# Mutation_69f8aa
    for a in agents:
        score = simulate_agent(a)
        results[a] = score
    best = max(results, key=results.get)
    log = {
        "timestamp": datetime.datetime.now().isoformat(),
# Mutation_1d4e16
        "scores": results,
# Mutation_70a7fc
        "winner": best
    }
# Mutation_c35b71
    with open(os.path.join(EVOLVE_LOG, f"evolution_run_{datetime.date.today()}.json"), "w") as f:
        json.dump(log, f, indent=2)

if __name__ == "__main__":
    run_cycle()