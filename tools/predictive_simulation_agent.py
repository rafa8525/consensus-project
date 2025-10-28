#!/usr/bin/env python3
"""
predictive_simulation_agent.py
Phase 5 – Predictive Simulation & Decision Autonomy
--------------------------------------------------
Analyzes historical subsystem logs, computes failure-risk scores,
and recommends or triggers pre-emptive actions.
"""

import os, re, datetime, statistics, json
BASE = "/home/rafa1215/consensus-project"
LOGS = f"{BASE}/memory/logs/system"
OUT = f"{BASE}/memory/logs/system/predictive_simulation.log"

TARGET_LOGS = [
    "vpn_test.log",
    "security_audit.log",
    "progress_evaluation.log",
    "heartbeat_monitor.log",
    "agent_evolution_cycle.log"
]

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(OUT, "a") as f: f.write(line + "\n")

def analyze_failures(path):
    if not os.path.exists(path): return 0
    with open(path) as f: text = f.read()
    fails = len(re.findall(r"FAIL|❌", text))
    total = max(1, len(re.findall(r"----", text)))
    return round((fails/total)*100, 2)

def main():
    log("---- Predictive Simulation Cycle Start ----")
    scores = {}
    for fname in TARGET_LOGS:
        fpath = os.path.join(LOGS, fname)
        risk = analyze_failures(fpath)
        scores[fname] = risk
        log(f"{fname}: {risk}% failure rate")

    avg = statistics.mean(scores.values())
    log(f"Average risk score: {avg:.2f}%")

    if avg >= 70:
        log("⚠️ High risk detected — triggering pre-emptive maintenance.")
        os.system(f"/usr/bin/python3 {BASE}/tools/master_control_loop.py --preemptive >> {OUT} 2>&1")
    elif avg >= 40:
        log("🟡 Moderate risk — system will tighten check frequency.")
    else:
        log("🟢 Low risk — no action required.")
    log("---- Predictive Simulation Cycle Complete ----\n")

    with open(f"{LOGS}/predictive_summary.json", "w") as f:
        json.dump({"scores": scores, "average": avg}, f, indent=2)

if __name__ == "__main__":
    main()
