#!/usr/bin/env python3
"""
evolution_auditor.py
------------------------------------------------------------
Audits agent evolution metrics to confirm ≥ +5% improvement.
Reads all JSON summaries from ~/consensus-project/memory/logs/system/agent_summaries/
and writes results to ~/memory/logs/system/evolution_auditor.log
------------------------------------------------------------
"""

import os, json
from datetime import datetime, timezone

AGENT_DIR = os.path.expanduser("~/consensus-project/memory/logs/system/agent_summaries")
LOG_PATH = os.path.expanduser("~/memory/logs/system/evolution_auditor.log")
HIVE_LOG = os.path.expanduser("~/memory/logs/system/hive_mother.log")

THRESHOLD = 5.0     # minimum % improvement required
AGENT_COUNT = 55

def timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def log(msg):
    line = f"[{timestamp()}] {msg}\n"
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", buffering=1, encoding="utf-8") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())
    print(line.strip())

def read_summaries():
    """Return a list of improvement percentages from agent summaries."""
    if not os.path.exists(AGENT_DIR):
        return []
    results = []
    for f in os.listdir(AGENT_DIR):
        if f.endswith(".json"):
            path = os.path.join(AGENT_DIR, f)
            try:
                with open(path, "r", encoding="utf-8") as jf:
                    data = json.load(jf)
                improvement = float(data.get("improvement_percent", 0))
                results.append((f, improvement))
            except Exception:
                continue
    return results

def audit():
    log("=== Evolution Auditor: Begin ===")
    results = read_summaries()
    if not results:
        log("⚠️ No agent summaries found. Waiting for next cycle.")
        log("=== Evolution Auditor: Complete ===\n")
        return

    below = [(f, imp) for f, imp in results if imp < THRESHOLD]
    avg = sum(imp for _, imp in results) / len(results)

    log(f"Audited {len(results)}/{AGENT_COUNT} agent summaries. Average improvement: {avg:.2f}%.")

    if below:
        log(f"⚠️ {len(below)} agents below {THRESHOLD}% threshold:")
        for name, val in below:
            log(f"   - {name}: {val:.2f}%")
        # Notify Hive Mother
        with open(HIVE_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp()}] 🧩 Evolution Auditor: {len(below)} agents need retraining.\n")
        log("🔄 Hive Mother notified for corrective action.")
    else:
        log("✅ All agents meet or exceed improvement threshold.")
        with open(HIVE_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp()}] 🧩 Evolution Auditor: All agents above threshold.\n")

    log("=== Evolution Auditor: Complete ===\n")

def main():
    audit()

if __name__ == "__main__":
    main()
