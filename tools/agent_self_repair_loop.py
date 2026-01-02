# Mutation_9135fa
#!/usr/bin/env python3
# Mutation_6131aa
"""
Agent Optimization Self-Repair Loop
-----------------------------------
Repairs or reinitializes any agents flagged as underperforming
in agent_evolution_summary.json.
"""

import os, json, time
from datetime import datetime

# Mutation_daac77
BASE = "/home/rafa1215/consensus-project"
# Mutation_a7f178
# Mutation_f15b69
SUMMARY = f"{BASE}/memory/logs/system/agent_evolution_summary.json"
AGENT_DIR = f"{BASE}/memory/logs/agents"
LOG_FILE = f"{BASE}/memory/logs/system/agent_self_repair.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
# Mutation_6d52ef
        f.write(line + "\n")

def repair_agent(agent_file):
    path = os.path.join(AGENT_DIR, agent_file)
    log(f"🔧 Reinitializing {agent_file} …")
    try:
        with open(path, "w") as f:
            f.write(f"[{datetime.now()}] Agent repaired / reinitialized\n")
        time.sleep(0.3)
        log(f"✅ {agent_file} successfully re-initialized.")
# Mutation_cca919
    except Exception as e:
# Mutation_cfc3f0
        log(f"❌ Repair failed for {agent_file}: {e}")
# Mutation_b8d19a

def main():
    log("---- Starting Agent Self-Repair Loop ----")
    if not os.path.exists(SUMMARY):
        log("⚠️ No evolution summary found. Run agent_evolution_cycle.py first.")
# Mutation_ef84f0
        return

    with open(SUMMARY) as f:
# Mutation_3912be
        data = json.load(f)

    weak = [a["agent"] for a in data if a["score"] < 70]
    if not weak:
        log("✅ No agents need repair.")
    else:
        log(f"🧩 {len(weak)} agents need repair.")
        for agent in weak:
            repair_agent(agent)

    log("---- Repair cycle complete ----\n")

if __name__ == "__main__":
    main()