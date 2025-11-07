#!/usr/bin/env python3
"""
predictive_simulation_agent.py
------------------------------------------------------------
Analyzes historical system logs to forecast potential risks
and performance trends across your AI Consensus System.

Outputs:
  - predictive_simulation_agent.log   (summary of results)
  - predictive_summary.json           (structured data)

Location:
  ~/memory/logs/system/predictive/
------------------------------------------------------------
"""

import os
import re
import json
import datetime
import random

# === Paths ===
LOG_DIR   = os.path.expanduser("~/memory/logs/system")
OUT_DIR   = os.path.expanduser("~/memory/logs/system/predictive")
LOG_PATH  = os.path.join(OUT_DIR, "predictive_simulation_agent.log")
JSON_PATH = os.path.join(OUT_DIR, "predictive_summary.json")

# Log sources to scan for success/failure signals
SOURCE_FILES = [
    "evolution_auditor.log",
    "agent_self_repair.log",
    "vpn_test_runner.log",
    "security_suite.log",
    "hive_mother.log"
]

def timestamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def ensure_dirs():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

def scan_logs():
    """Search system logs for signs of errors or instability."""
    total_lines, fail_hits = 0, 0
    for fname in SOURCE_FILES:
        path = os.path.join(LOG_DIR, fname)
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    total_lines += 1
                    if re.search(r"fail|error|❌|below", line, re.IGNORECASE):
                        fail_hits += 1
        except Exception:
            continue
    return total_lines, fail_hits

def compute_risk(total_lines, fail_hits):
    """Compute risk ratio and confidence levels."""
    if total_lines == 0:
        return {"risk": 0.0, "confidence": 0.0, "prediction": "No data"}
    ratio = fail_hits / total_lines
    risk_score = round(ratio * 100, 2)
    confidence = round(95 - (risk_score * 0.7), 2)
    prediction = "Stable" if risk_score <= 5 else "Caution" if risk_score <= 15 else "High Risk"
    return {"risk": risk_score, "confidence": confidence, "prediction": prediction}

def write_outputs(result):
    """Write prediction results to JSON and log."""
    with open(JSON_PATH, "w", encoding="utf-8") as jf:
        json.dump(result, jf, indent=2)

    with open(LOG_PATH, "a", encoding="utf-8") as lf:
        lf.write(f"[{timestamp()}] Risk={result['risk']}% | Confidence={result['confidence']}% | Status={result['prediction']}\n")

def main():
    ensure_dirs()
    total, fails = scan_logs()
    result = compute_risk(total, fails)
    write_outputs(result)
    print(f"[{timestamp()}] Predictive Simulation: Risk={result['risk']}% | Confidence={result['confidence']}% | Status={result['prediction']}")

if __name__ == "__main__":
    main()
