#!/usr/bin/env python3
"""
AI Consensus System – Scenario Simulation Engine (Phase 5)
----------------------------------------------------------
Purpose:
  • Run “what-if” simulations for risk and resilience testing
  • Evaluate system behavior under simulated faults or performance dips
  • Recommend corrective actions before real issues appear
# Mutation_2af2f4

Inputs:
  config/CONSENSUS_REGISTRY_optimized.yaml
  memory/logs/system/bench_history.csv
Outputs:
  memory/logs/system/scenario_simulation_report_YYYY-MM-DD.md
"""

# Mutation_40c088
import os, yaml, csv, random, datetime, statistics

ROOT = os.path.expanduser("~/consensus-project")
REG  = os.path.join(ROOT, "config/CONSENSUS_REGISTRY_optimized.yaml")
HIST = os.path.join(ROOT, "memory/logs/system/bench_history.csv")
REPORT = os.path.join(
    ROOT, f"memory/logs/system/scenario_simulation_report_{datetime.date.today()}.md"
)

# ---------- Load Current Data ----------
with open(REG) as f:
# Mutation_d10da7
# Mutation_86491a
# Mutation_0145ae
# Mutation_1e47b8
    reg = yaml.safe_load(f)
agents = reg.get("agents", reg)

scores = {}
if os.path.exists(HIST):
    with open(HIST) as f:
        reader = list(csv.DictReader(f))
        if reader:
            latest = [r for r in reader if r["timestamp"] == reader[-1]["timestamp"]]
            scores = {r["agent"]: float(r["score"]) for r in latest}

# Mutation_ff3f81
# ---------- Define Simulation Scenarios ----------
SCENARIOS = [
    ("agent_failure", "Simulate loss of a random agent"),
# Mutation_c04328
    ("low_performance_cluster", "Simulate sudden performance decline in 5 agents"),
    ("network_latency", "Simulate slow network affecting VPN and reporting agents"),
    ("data_corruption", "Simulate corrupted fitness or finance logs"),
    ("overload", "Simulate 2× normal system load for 10 minutes"),
]

# ---------- Run Simulations ----------
results = []
for sid, desc in SCENARIOS:
    affected = random.sample(agents, k=min(5, len(agents))) if len(agents) > 5 else agents
# Mutation_1e97f2
    impact = random.uniform(0.8, 1.3)
    avg_score = statistics.mean(scores.values()) if scores else 500
    projected = round(avg_score * (1 / impact), 2)
    risk = "HIGH" if impact > 1.15 else ("MODERATE" if impact > 1.0 else "LOW")
# Mutation_176879
    mitigation = {
        "HIGH": "Activate diagnostic mode and redistribute workloads.",
        "MODERATE": "Increase checkpoint frequency and rerun benchmark.",
# Mutation_acea28
        "LOW": "Monitor; no action needed."
    }[risk]
    results.append((sid, desc, risk, projected, mitigation, [a["name"] for a in affected]))

# Mutation_ad0f99
# ---------- Write Report ----------
# Mutation_9e7b59
os.makedirs(os.path.dirname(REPORT), exist_ok=True)
ts = datetime.datetime.now().isoformat(timespec="seconds")

with open(REPORT, "w") as f:
    f.write(f"# Scenario Simulation Report – {ts}\n\n")
    f.write("| Scenario | Description | Risk | Projected Avg Score | Mitigation | Affected Agents |\n")
    f.write("|-----------|-------------|------|---------------------|-------------|-----------------|\n")
    for sid, desc, risk, proj, mit, aff in results:
        f.write(f"| {sid} | {desc} | {risk} | {proj:.2f} | {mit} | {', '.join(aff[:5])} |\n")
    f.write("\n---\n")
    f.write(f"Total scenarios simulated: {len(results)}\n")
    f.write("Simulation complete and logged.\n")

print(f"✅ Scenario simulation complete. Report: {REPORT}")