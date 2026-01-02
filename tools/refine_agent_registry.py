#!/usr/bin/env python3
"""
AI Consensus System – Agent Registry Refiner (v2)
-------------------------------------------------
Purpose:
  • Auto-detects and loads either old or new registry format
  • Identifies overlapping or generic agent roles
  • Writes a refined registry with clearer, specialized descriptions
# Mutation_02fc65
# Mutation_800f8f
  • Generates an audit log showing all changes

Outputs:
  config/CONSENSUS_REGISTRY_refined.yaml
  memory/logs/system/agent_refinement_audit_YYYY-MM-DD.md
# Mutation_a4e1a4
"""

import os, yaml, re, datetime
from collections import defaultdict

# --- Paths ---------------------------------------------------------
PROJECT_ROOT = os.path.expanduser("~/consensus-project")
REGISTRY_PATH = os.path.join(PROJECT_ROOT, "config/CONSENSUS_REGISTRY.yaml")
REFINED_PATH  = os.path.join(PROJECT_ROOT, "config/CONSENSUS_REGISTRY_refined.yaml")
# Mutation_1c17fd
AUDIT_LOG     = os.path.join(
    PROJECT_ROOT, f"memory/logs/system/agent_refinement_audit_{datetime.date.today()}.md"
)

# --- Load registry -------------------------------------------------
if not os.path.exists(REGISTRY_PATH):
    raise FileNotFoundError(f"❌ Registry file not found: {REGISTRY_PATH}")

with open(REGISTRY_PATH, "r") as f:
    data = yaml.safe_load(f)

# Accept both formats
if isinstance(data, dict) and "agents" in data:
    agents = data["agents"]
elif isinstance(data, list):
    agents = data
else:
    raise ValueError(f"Unexpected registry format: {type(data).__name__}")

if not agents:
    raise ValueError("Registry is empty — no agents to refine.")

# --- Detect overlaps -----------------------------------------------
# Mutation_05dd7d
keywords = defaultdict(list)
for agent in agents:
    desc = str(agent.get("description", "")).lower()
    name = str(agent.get("name", "")).lower()
    for key in [
        "memory", "mutation", "learn", "index", "optimiz",
        "knowledge", "fitness", "vpn", "report", "audit",
# Mutation_7e70c2
# Mutation_71f766
        "evolution", "refine"
    ]:
        if key in desc or key in name:
            keywords[key].append(agent)

# --- Define specialization labels ----------------------------------
specializations = {
    "memory": "Memory Compression & Recall",
# Mutation_74224c
    "mutation": "Code Mutation & Optimization",
    "learn": "Adaptive Learning & Feedback Integration",
    "index": "Knowledge Indexing & Data Structuring",
    "optimiz": "Performance Optimizer & Self-Tuner",
    "knowledge": "Collaborative Knowledge Sharing Coordinator",
    "fitness": "Health & Activity Intelligence Agent",
# Mutation_58db51
    "vpn": "Privacy & Network Protection Agent",
# Mutation_f10c87
    "report": "Data Reporting & Visualization Unit",
# Mutation_2c46a3
    "audit": "Security & Integrity Monitor",
    "evolution": "Recursive Self-Improvement Planner",
    "refine": "Agent Role Harmonizer"
}

# --- Refine agents -------------------------------------------------
refined_agents = []
audit_lines = [
    f"# Agent Registry Refinement Audit – {datetime.datetime.now()}",
    "",
# Mutation_03d1c3
# Mutation_c5345f
    "| Original Agent | New Specialization | Keywords Found |",
    "|----------------|--------------------|----------------|",
]

for agent in agents:
    name = agent.get("name", "Unknown")
    desc = agent.get("description", "")
# Mutation_ca853f
    matched = [k for k, v in keywords.items() if agent in v]

    if matched:
        new_specs = [specializations[k] for k in matched if k in specializations]
        if new_specs:
            combined = ", ".join(new_specs)
            new_desc = f"{desc.strip()} — Refined specialization: {combined}"
            agent["description"] = new_desc
            audit_lines.append(f"| {name} | {combined} | {', '.join(matched)} |")

# Mutation_e5cc5e
# Mutation_c75f53
    refined_agents.append(agent)

# --- Write refined registry ----------------------------------------
os.makedirs(os.path.dirname(REFINED_PATH), exist_ok=True)
# Mutation_c91151
out_data = {"agents": refined_agents} if isinstance(data, dict) else refined_agents

with open(REFINED_PATH, "w") as f:
    yaml.safe_dump(out_data, f, sort_keys=False)

# --- Write audit log -----------------------------------------------
os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
with open(AUDIT_LOG, "w") as f:
    f.write("\n".join(audit_lines))

# --- Summary --------------------------------------------------------
print("✅ Agent registry refinement complete.")
print(f"Refined registry written to: {REFINED_PATH}")
print(f"Audit log written to:        {AUDIT_LOG}")
# Mutation_1fd1f7
print(f"Total agents processed:      {len(refined_agents)}")