#!/usr/bin/env python3
"""
hive_summary_integrator.py
------------------------------------------------------------
Consolidates daily reports from all system modules:
- Hive Mother
- Enhancement Tracker
- Evolution Auditor
- Predictive Agents (Task Flow, Simulation, Scenario)

Outputs:
  ~/memory/logs/system/hive_summary.log
------------------------------------------------------------
"""

import os
import json
from datetime import datetime, timezone

# === File Paths ===
BASE = os.path.expanduser("~/consensus-project")
LOG_DIR = os.path.expanduser("~/memory/logs/system")
HIVE_LOG = os.path.join(LOG_DIR, "hive_mother.log")
ENHANCE_LOG = os.path.join(LOG_DIR, "enhancement_tracker.log")
EVOL_LOG = os.path.join(LOG_DIR, "evolution_auditor.log")
SUMMARY_PATH = os.path.join(LOG_DIR, "hive_summary.log")
ENHANCE_INDEX = os.path.join(BASE, "memory/logs/system/enhancement_index.json")

# Predictive subfolder
PRED_DIR = os.path.join(LOG_DIR, "predictive")
SCEN_JSON = os.path.join(PRED_DIR, "scenario_summary.json")
TASK_JSON = os.path.join(PRED_DIR, "predictive_task_flow.json")
SIM_JSON  = os.path.join(PRED_DIR, "predictive_summary.json")

# === Helpers ===
def timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def read_last_lines(path, n=5):
    """Return the last n lines from a file if available."""
    if not os.path.exists(path):
        return [f"[{timestamp()}] (no log found)\n"]
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        return lines[-n:] if lines else [f"[{timestamp()}] (empty)\n"]

def summarize_enhancements():
    """Count enhancements from the JSON index."""
    if not os.path.exists(ENHANCE_INDEX):
        return 0
    try:
        with open(ENHANCE_INDEX, "r", encoding="utf-8") as f:
            data = json.load(f)
        return len(data)
    except Exception:
        return 0

def read_json(path):
    """Safe JSON loader with fallback."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def write_summary(summary):
    """Append summary to main Hive summary log."""
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "a", encoding="utf-8") as f:
        f.write(summary + "\n")
    print(summary)

# === Main Summary Logic ===
def compile_digest():
    """Merge insights from all layers into one report."""
    enh_count = summarize_enhancements()
    hive_recent = "".join(read_last_lines(HIVE_LOG, 5))
    evol_recent = "".join(read_last_lines(EVOL_LOG, 5))
    enhance_recent = "".join(read_last_lines(ENHANCE_LOG, 3))

    digest = (
        f"\n=== Hive Mother Daily Summary ({timestamp()}) ===\n"
        f"Enhancements Logged: {enh_count}\n\n"
        f"--- Hive Mother ---\n{hive_recent}\n"
        f"--- Evolution Auditor ---\n{evol_recent}\n"
        f"--- Enhancement Tracker ---\n{enhance_recent}\n"
    )

    # --- Predictive Summary Integration ---
    task_data = read_json(TASK_JSON)
    sim_data  = read_json(SIM_JSON)
    scen_data = read_json(SCEN_JSON)

    if scen_data:
        outlook = scen_data.get("outlook", "N/A")
        conf = scen_data.get("confidence", "N/A")
        risk = scen_data.get("risk_score", "N/A")
    else:
        outlook, conf, risk = "N/A", "N/A", "N/A"

    digest += (
        "--- Predictive Summary ---\n"
        f"Outlook={outlook} | Confidence={conf}% | Risk={risk}%\n"
        f"Task Confidence={task_data.get('confidence', 'N/A')} | "
        f"Simulation Confidence={sim_data.get('confidence', 'N/A')}%\n"
    )

    digest += "Summary compiled successfully.\n===============================\n"

    write_summary(digest)

def main():
    print(f"[{timestamp()}] [INFO] Generating unified Hive Mother summary...")
    compile_digest()
    print(f"[{timestamp()}] [INFO] Summary complete.")

if __name__ == "__main__":
    main()
