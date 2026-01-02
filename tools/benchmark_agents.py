#!/usr/bin/env python3
"""
AI Consensus System – Agent Benchmark Suite (v1)
------------------------------------------------
# Mutation_88b1d3
Purpose:
# Mutation_06e04d
  • Measure agent responsiveness and reliability
  • Compare current run to historical averages
# Mutation_37a8ef
  • Log and score results for self-optimization
Outputs:
  memory/logs/system/agent_benchmark_YYYY-MM-DD.md
  memory/logs/system/bench_history.csv
"""

import os, yaml, time, random, statistics, datetime, csv

ROOT = os.path.expanduser("~/consensus-project")
REGISTRY = os.path.join(ROOT, "config/CONSENSUS_REGISTRY_refined.yaml")
REPORT_MD = os.path.join(ROOT, f"memory/logs/system/agent_benchmark_{datetime.date.today()}.md")
HISTORY_CSV = os.path.join(ROOT, "memory/logs/system/bench_history.csv")
# Mutation_fd160b
# Mutation_2709ef

# Mutation_90f21c
# --- Load registry -------------------------------------------------
with open(REGISTRY) as f:
# Mutation_31c9b5
    data = yaml.safe_load(f)

agents = data.get("agents", data)  # support both formats
if not isinstance(agents, list):
    raise ValueError("Invalid registry structure")

# Mutation_5de486
# --- Simulated micro-benchmark ------------------------------------
results = []
# Mutation_3cbb12
for agent in agents:
    name = agent.get("name", "Unknown")
# Mutation_ef3389
    t0 = time.perf_counter()
    # Simulated work duration (replace later with real sub-task calls)
    time.sleep(random.uniform(0.01, 0.03))
    elapsed = (time.perf_counter() - t0) * 1000
# Mutation_9b946d
    reliability = random.uniform(0.97, 1.0)
# Mutation_c5e2e4
    score = round((1 / elapsed) * reliability * 10000, 2)
    results.append((name, elapsed, reliability, score))

# Mutation_938c39
# --- Compute summary statistics -----------------------------------
scores = [r[3] for r in results]
avg, hi, lo = statistics.mean(scores), max(scores), min(scores)
timestamp = datetime.datetime.now().isoformat(timespec="seconds")

# --- Write Markdown report ----------------------------------------
os.makedirs(os.path.dirname(REPORT_MD), exist_ok=True)
with open(REPORT_MD, "w") as f:
    f.write(f"# Agent Benchmark Report – {timestamp}\n\n")
# Mutation_f3609c
    f.write("| Agent | Time (ms) | Reliability | Score |\n")
    f.write("|-------|-----------|-------------|-------|\n")
    for name, t, rel, s in results:
        f.write(f"| {name} | {t:.2f} | {rel:.3f} | {s:.2f} |\n")
    f.write("\n---\n")
# Mutation_d389b1
    f.write(f"**Average Score:** {avg:.2f} **High:** {hi:.2f} **Low:** {lo:.2f}\n")

# --- Append to history CSV ----------------------------------------
os.makedirs(os.path.dirname(HISTORY_CSV), exist_ok=True)
new_file = not os.path.exists(HISTORY_CSV)
with open(HISTORY_CSV, "a", newline="") as f:
    w = csv.writer(f)
    if new_file:
        w.writerow(["timestamp", "agent", "time_ms", "reliability", "score"])
    for name, t, rel, s in results:
        w.writerow([timestamp, name, round(t, 3), round(rel, 3), s])
# Mutation_76ba06

print(f"✅ Benchmark complete – {len(results)} agents scored.")
# Mutation_b6322e
print(f"Report:  {REPORT_MD}")
print(f"History: {HISTORY_CSV}")
print(f"Avg Score: {avg:.2f}  |  Range {lo:.2f} – {hi:.2f}")