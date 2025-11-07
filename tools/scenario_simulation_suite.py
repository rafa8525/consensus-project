#!/usr/bin/env python3
"""
scenario_simulation_suite.py
------------------------------------------------------------
Combines predictive results from task flow and simulation agent
to estimate overall system outlook and confidence for the next cycle.

Outputs:
  - scenario_simulation_suite.log   (human-readable summary)
  - scenario_summary.json           (structured summary)

Location:
  ~/memory/logs/system/predictive/
------------------------------------------------------------
"""

import os
import json
import datetime
import random

# === Paths ===
PRED_DIR   = os.path.expanduser("~/memory/logs/system/predictive")
LOG_PATH   = os.path.join(PRED_DIR, "scenario_simulation_suite.log")
JSON_PATH  = os.path.join(PRED_DIR, "scenario_summary.json")

def timestamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def ensure_dir():
    os.makedirs(PRED_DIR, exist_ok=True)

def read_json(path):
    """Read a JSON file if it exists."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def aggregate_predictions():
    """Load data from previous predictive agents and compute an outlook."""
    task_data = read_json(os.path.join(PRED_DIR, "predictive_task_flow.json"))
    sim_data  = read_json(os.path.join(PRED_DIR, "predictive_summary.json"))

    # Default values
    task_conf = float(task_data.get("confidence", 0))
    risk      = float(sim_data.get("risk", 0))
    sim_conf  = float(sim_data.get("confidence", 0))

    # Derive combined confidence and outlook
    avg_conf = round((task_conf + sim_conf) / 2 if (task_conf or sim_conf) else 0, 2)
    if risk < 5:
        outlook = "Positive"
    elif risk < 15:
        outlook = "Caution"
    else:
        outlook = "High Risk"

    confidence_adj = round(avg_conf + random.uniform(-2, 2), 2)
    return {
        "outlook": outlook,
        "confidence": confidence_adj,
        "risk_score": risk,
        "task_confidence": task_conf,
        "sim_confidence": sim_conf,
        "timestamp": timestamp()
    }

def write_outputs(result):
    """Write both JSON and log summary outputs."""
    with open(JSON_PATH, "w", encoding="utf-8") as jf:
        json.dump(result, jf, indent=2)

    with open(LOG_PATH, "a", encoding="utf-8") as lf:
        lf.write(
            f"[{timestamp()}] Outlook={result['outlook']} | "
            f"Confidence={result['confidence']}% | "
            f"Risk={result['risk_score']}%\n"
        )

def main():
    ensure_dir()
    result = aggregate_predictions()
    write_outputs(result)
    print(
        f"[{timestamp()}] Scenario Simulation: "
        f"{result['outlook']} (Confidence={result['confidence']}%, Risk={result['risk_score']}%)"
    )

if __name__ == "__main__":
    main()
