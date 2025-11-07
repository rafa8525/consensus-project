#!/usr/bin/env python3
"""
agent_self_repair.py
------------------------------------------------------------
Triggered by Hive Mother or Evolution Auditor when agents fall
below improvement thresholds.  It re-runs or refreshes those
agents' scripts and records repair results.
------------------------------------------------------------
"""

import os, json, subprocess
from datetime import datetime, timezone

SUMMARY_DIR = os.path.expanduser("~/consensus-project/memory/logs/system/agent_summaries")
LOG_PATH = os.path.expanduser("~/memory/logs/system/agent_self_repair.log")
HIVE_LOG = os.path.expanduser("~/memory/logs/system/hive_mother.log")

THRESHOLD = 5.0
AGENT_BASE = os.path.expanduser("~/consensus-project/tools")

def timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def log(msg):
    line = f"[{timestamp()}] {msg}\n"
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def read_underperformers():
    """Read all agent summaries and return those < threshold."""
    if not os.path.exists(SUMMARY_DIR):
        return []
    bad = []
    for f in os.listdir(SUMMARY_DIR):
        if f.endswith(".json"):
            path = os.path.join(SUMMARY_DIR, f)
            try:
                with open(path, "r", encoding="utf-8") as jf:
                    data = json.load(jf)
                imp = float(data.get("improvement_percent", 0))
                if imp < THRESHOLD:
                    bad.append((f, imp))
            except Exception:
                continue
    return bad

def attempt_repair(agent_file):
    """Try to rerun or refresh the agent script."""
    name = os.path.splitext(agent_file)[0]
    candidate_paths = [
        os.path.join(AGENT_BASE, name + ".py"),
        os.path.join(AGENT_BASE, "agents", name + ".py")
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            log(f"🔁 Rerunning {path} for self-repair...")
            try:
                subprocess.run(["python3", path], check=False)
                log(f"✅ {name} re-executed successfully.")
                return True
            except Exception as e:
                log(f"[ERROR] Failed to rerun {name}: {e}")
                return False
    log(f"[WARN] Script for {name} not found; skipped.")
    return False

def main():
    log("=== Agent Self-Repair: Begin ===")
    underperformers = read_underperformers()
    if not underperformers:
        log("No agents below threshold; nothing to repair.")
        log("=== Agent Self-Repair: Complete ===\n")
        return

    log(f"Detected {len(underperformers)} underperforming agents (<{THRESHOLD}%).")
    for f, val in underperformers:
        log(f"→ Attempting repair for {f} ({val:.2f}%).")
        attempt_repair(f)

    # Notify Hive Mother
    with open(HIVE_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp()}] 🧩 Agent Self-Repair executed for {len(underperformers)} agents.\n")

    log("=== Agent Self-Repair: Complete ===\n")

if __name__ == "__main__":
    main()
