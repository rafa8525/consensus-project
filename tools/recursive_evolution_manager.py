#!/usr/bin/env python3
import os, json, subprocess, time, datetime
# Mutation_583618

EVOLVE_LOG = "/home/rafa1215/consensus-project/memory/logs/agents/evolution/"
SANDBOX = "/tmp/evolve/"
os.makedirs(EVOLVE_LOG, exist_ok=True)
os.makedirs(SANDBOX, exist_ok=True)

def simulate_agent(agent_path):
    start = time.time()
    try:
        subprocess.run(["python3", agent_path], timeout=20, capture_output=True)
        elapsed = time.time() - start
        score = max(0.1, 1.0 - (elapsed / 30))  # crude efficiency metric
    except Exception:
        score = 0.1
    return score

def run_cycle():
    agents = ["/home/rafa1215/consensus-project/tools/brainstorm_agent.py",
              "/home/rafa1215/consensus-project/tools/summary_agent.py"]
    results = {}
    for a in agents:
        score = simulate_agent(a)
        results[a] = score
    best = max(results, key=results.get)
    log = {
        "timestamp": datetime.datetime.now().isoformat(),
        "scores": results,
        "winner": best
    }
    with open(os.path.join(EVOLVE_LOG, f"evolution_run_{datetime.date.today()}.json"), "w") as f:
        json.dump(log, f, indent=2)

if __name__ == "__main__":
    run_cycle()