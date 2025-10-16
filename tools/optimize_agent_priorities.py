#!/usr/bin/env python3
"""
AI Consensus System – Adaptive Self-Optimization (Phase 3)
-----------------------------------------------------------
Purpose:
  • Use latest benchmark scores to adjust agent priorities
  • Write updated registry + audit log
Inputs:
  memory/logs/system/bench_history.csv
  config/CONSENSUS_REGISTRY_refined.yaml
Outputs:
  config/CONSENSUS_REGISTRY_optimized.yaml
  memory/logs/system/agent_priority_audit_YYYY-MM-DD.md
"""
import os, csv, statistics, datetime, yaml

ROOT = os.path.expanduser("~/consensus-project")
HIST = os.path.join(ROOT, "memory/logs/system/bench_history.csv")
REG  = os.path.join(ROOT, "config/CONSENSUS_REGISTRY_refined.yaml")
OUT  = os.path.join(ROOT, "config/CONSENSUS_REGISTRY_optimized.yaml")
AUD  = os.path.join(ROOT, f"memory/logs/system/agent_priority_audit_{datetime.date.today()}.md")

# --- Load latest scores --------------------------------------------
scores = {}
with open(HIST) as f:
    reader = list(csv.DictReader(f))
    latest = [r for r in reader if r["timestamp"] == reader[-1]["timestamp"]]
    for r in latest:
        scores[r["agent"]] = float(r["score"])

mean = statistics.mean(scores.values())
hi, lo = mean * 1.10, mean * 0.90

# --- Load registry -------------------------------------------------
with open(REG) as f:
    data = yaml.safe_load(f)
agents = data.get("agents", data)

# --- Adjust priorities ---------------------------------------------
audit = [
    f"# Agent Priority Optimization – {datetime.datetime.now()}",
    "",
    f"Average Score: {mean:.2f} High >{hi:.2f} Low <{lo:.2f}",
    "",
    "| Agent | Score | Old Priority | New Priority |",
    "|--------|--------|---------------|---------------|"
]
for a in agents:
    name = a.get("name")
    s = scores.get(name)
    if s is None: continue
    old = a.get("priority", 5)
    if s >= hi:
        new = min(old + 1, 10)
    elif s <= lo:
        new = max(old - 1, 1)
    else:
        new = old
    a["priority"] = new
    audit.append(f"| {name} | {s:.2f} | {old} | {new} |")

# --- Write outputs -------------------------------------------------
os.makedirs(os.path.dirname(OUT), exist_ok=True)
yaml.safe_dump({"agents": agents}, open(OUT, "w"), sort_keys=False)
os.makedirs(os.path.dirname(AUD), exist_ok=True)
open(AUD, "w").write("\n".join(audit))

print(f"✅ Optimization complete. Mean {mean:.2f}")
print(f"New registry: {OUT}")
print(f"Audit log:   {AUD}")
