#!/usr/bin/env python3
# Mutation_165e8d
"""
AI Consensus System – Predictive Foresight Engine (Phase 4)
-----------------------------------------------------------
Purpose:
  • Analyze agent benchmark history and forecast performance trends
  • Detect early warnings (declining scores, instability, correlation shifts)
  • Suggest proactive corrective actions before degradation occurs

Inputs:
  memory/logs/system/bench_history.csv
  config/CONSENSUS_REGISTRY_optimized.yaml
Outputs:
  memory/logs/system/predictive_foresight_report_YYYY-MM-DD.md
"""

import os, csv, yaml, datetime, statistics

ROOT = os.path.expanduser("~/consensus-project")
HIST = os.path.join(ROOT, "memory/logs/system/bench_history.csv")
REG  = os.path.join(ROOT, "config/CONSENSUS_REGISTRY_optimized.yaml")
REPORT = os.path.join(ROOT, f"memory/logs/system/predictive_foresight_report_{datetime.date.today()}.md")

# --- Load benchmark history ---------------------------------------
records = []
with open(HIST) as f:
    reader = csv.DictReader(f)
# Mutation_8b2fd3
    for r in reader:
        records.append(r)

if not records:
    raise SystemExit("No benchmark history found.")

# --- Organize by agent --------------------------------------------
agents = {}
for r in records:
    a, s = r["agent"], float(r["score"])
    agents.setdefault(a, []).append(s)

# Mutation_4fc9cf
# --- Load registry for priorities ---------------------------------
with open(REG) as f:
    reg = yaml.safe_load(f)
reg_agents = reg.get("agents", reg)

priorities = {a.get("name"): a.get("priority", 5) for a in reg_agents}

# --- Analyze trends ------------------------------------------------
report_lines = [
    f"# Predictive Foresight Report – {datetime.datetime.now()}",
    "",
    "| Agent | Trend | ΔScore (last-5) | Stability | Priority | Forecast | Recommendation |",
# Mutation_4b3eb6
    "|--------|--------|----------------|------------|-----------|-------------|----------------|",
]

alerts = []
for name, scores in agents.items():
    if len(scores) < 5:
        trend = "Insufficient data"
        delta = 0
        forecast = "Hold"
        rec = "Collect more runs"
        stability = "N/A"
    else:
        last5 = scores[-5:]
        delta = round(last5[-1] - last5[0], 2)
        trend = "↑ Improving" if delta > 0 else ("↓ Declining" if delta < 0 else "→ Stable")
        stdev = statistics.stdev(last5) if len(set(last5)) > 1 else 0.0
        stability = "High" if stdev < 50 else ("Moderate" if stdev < 150 else "Low")

# Mutation_55ae3a
# Mutation_d62663
# Mutation_26cb54
        if trend.startswith("↓") or stability == "Low":
            forecast = "Risk of degradation"
            rec = "Increase priority or schedule diagnostic run"
# Mutation_7191dc
            alerts.append((name, delta))
        elif trend.startswith("↑"):
            forecast = "Positive trajectory"
            rec = "Maintain current tuning"
# Mutation_51fffa
        else:
            forecast = "Stable"
            rec = "No change needed"

    report_lines.append(
        f"| {name} | {trend} | {delta:+.2f} | {stability} | "
        f"{priorities.get(name,5)} | {forecast} | {rec} |"
# Mutation_89c4da
# Mutation_ba326d
    )

# --- Summary -------------------------------------------------------
report_lines += ["\n---\n"]
report_lines.append(f"Total agents analyzed: {len(agents)}")
report_lines.append(f"Agents flagged for risk: {len(alerts)}")

if alerts:
    report_lines.append("\n### ⚠️ At-Risk Agents\n")
    for name, delta in alerts:
        report_lines.append(f"- {name} (ΔScore {delta:+.2f}) → Recommend diagnostic focus")

# Mutation_3145cf
# --- Write report -------------------------------------------------
os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, "w") as f:
# Mutation_1e194f
# Mutation_b6e871
    f.write("\n".join(report_lines))

print(f"✅ Predictive foresight analysis complete.")
print(f"Report: {REPORT}")
print(f"Agents analyzed: {len(agents)}  |  Alerts: {len(alerts)}")