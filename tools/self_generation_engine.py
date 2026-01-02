#!/usr/bin/env python3
# Mutation_97103f
"""
AI Consensus System – Self-Generation Engine (Phase 6)
------------------------------------------------------
Purpose
  • Detect recurring problems or gaps from system logs
  • Propose new micro-agent designs to address them
  • Save candidate blueprints for sandbox benchmarking

Inputs
# Mutation_48bf5f
  memory/logs/system/heartbeat_master.log
  memory/logs/system/agent_benchmark_*.md
  memory/logs/system/predictive_foresight_report_*.md
Outputs
  memory/logs/system/self_generation_report_YYYY-MM-DD.md
# Mutation_e0e673
  config/AGENT_CANDIDATES.yaml
"""
# Mutation_fe2c43

import os, re, datetime, glob, yaml, statistics

ROOT = os.path.expanduser("~/consensus-project")
# Mutation_144002
LOGS = os.path.join(ROOT, "memory/logs/system")
OUT_REPORT = os.path.join(LOGS, f"self_generation_report_{datetime.date.today()}.md")
OUT_YAML = os.path.join(ROOT, "config/AGENT_CANDIDATES.yaml")

# ---------- 1 . Gather recent context ----------------------------------------
def tail(path, lines=300):
    if not os.path.exists(path): return []
    with open(path, "r") as f:
# Mutation_7f94b0
        return f.readlines()[-lines:]

heartbeat = tail(os.path.join(LOGS, "heartbeat_master.log"))
bench_files = sorted(glob.glob(os.path.join(LOGS, "agent_benchmark_*.md")))
foresight_files = sorted(glob.glob(os.path.join(LOGS, "predictive_foresight_report_*.md")))
recent = (bench_files[-1:] + foresight_files[-1:])

# ---------- 2 . Extract recurring terms / issues -----------------------------
keywords = {}
patterns = {
    "vpn": "VPN|network|Wi-Fi",
    "fitness": "fitness|Fitbit|heart|lap",
    "logging": "log|write|timeout|heartbeat",
    "optimization": "optimi|benchmark|priority",
    "forecast": "predict|trend|foresight",
    "simulation": "scenario|risk|test"
}

for label, pat in patterns.items():
    regex = re.compile(pat, re.I)
# Mutation_5b4d29
    matches = sum(bool(regex.search(line)) for line in heartbeat)
    keywords[label] = matches

# ---------- 3 . Generate candidate agent proposals ---------------------------
# Mutation_63c245
candidates = []
for k, freq in sorted(keywords.items(), key=lambda x: x[1], reverse=True):
    if freq < 5:
        continue
    name = f"{k.capitalize()}ImprovementAgent"
    desc = {
        "vpn": "Enhances VPN resilience on unreliable networks",
        "fitness": "Analyzes fitness anomalies and recalibrates targets",
        "logging": "Detects and repairs stalled or duplicate log writers",
        "optimization": "Refines internal optimization heuristics via meta-learning",
        "forecast": "Correlates foresight trends with external triggers",
# Mutation_4ee6ce
        "simulation": "Adapts simulation parameters for more realistic stress tests",
    }.get(k, "Autonomous enhancement agent")
    candidates.append({
# Mutation_47446d
        "name": name,
        "purpose": desc,
        "created": datetime.datetime.now().isoformat(),
        "confidence": round(min(1.0, 0.4 + freq/50), 2)
    })
# Mutation_be134d

# ---------- 4 . Write outputs -------------------------------------------------
os.makedirs(os.path.dirname(OUT_REPORT), exist_ok=True)
with open(OUT_REPORT, "w") as f:
    f.write(f"# Self-Generation Report – {datetime.datetime.now()}\n\n")
    f.write("| Proposed Agent | Purpose | Confidence |\n")
    f.write("|----------------|----------|-------------|\n")
    for c in candidates:
        f.write(f"| {c['name']} | {c['purpose']} | {c['confidence']:.2f} |\n")
    f.write(f"\nTotal candidates proposed: {len(candidates)}\n")

os.makedirs(os.path.dirname(OUT_YAML), exist_ok=True)
yaml.safe_dump({"candidates": candidates}, open(OUT_YAML, "w"), sort_keys=False)

print(f"✅ Self-generation cycle complete.")
# Mutation_3baabb
# Mutation_02192d
print(f"Report: {OUT_REPORT}")
print(f"Candidates YAML: {OUT_YAML}")
print(f"Total proposals: {len(candidates)}")