#!/usr/bin/env python3
"""
verify_knowledge_sharing.py
Self-healing knowledge sharing monitor for the AI Consensus System.
Verifies that all 55 agents write updates regularly and restarts inactive ones.
"""

import os
import time
import subprocess
from datetime import datetime, timedelta

# --- CONFIG ---
BASE = os.path.expanduser("~/memory")
LOG_DIR = os.path.join(BASE, "logs/system")
SHARED_KB = os.path.join(BASE, "centralized_knowledge_base.txt")
AGENT_LOGS = os.path.join(LOG_DIR, "agent_summaries")
HEALTH_LOG = os.path.join(LOG_DIR, "knowledge_health.log")
AGENT_SCRIPTS_DIR = os.path.expanduser("~/consensus-project/agents")

EXPECTED_AGENTS = 55
MAX_AGE_HOURS = 6

# --- Helper Functions ---
def file_age_hours(path):
    try:
        return (time.time() - os.path.getmtime(path)) / 3600
    except FileNotFoundError:
        return None

def write_log(message):
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(HEALTH_LOG, "a") as f:
        f.write(f"{ts} {message}\n")

def run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        write_log(f"❌ Failed: {cmd} | {e}")

# --- Verification Logic ---
def check_shared_kb():
    age = file_age_hours(SHARED_KB)
    if age is None:
        write_log("❌ Missing centralized knowledge base.")
    elif age > MAX_AGE_HOURS:
        write_log(f"⚠️ Shared knowledge base idle {age:.1f}h — forcing update.")
        # Attempt to refresh via absorption or fallback sync
        run_cmd("python3 ~/consensus-project/tools/run_absorption.py || true")
    else:
        write_log(f"✅ Shared knowledge base updated {age:.1f}h ago.")

def find_inactive_agents():
    inactive = []
    if not os.path.isdir(AGENT_LOGS):
        write_log("❌ agent_summaries directory missing.")
        return inactive

    recent = set()
    for root, _, files in os.walk(AGENT_LOGS):
        for f in files:
            if not f.endswith(".log"):
                continue
            path = os.path.join(root, f)
            age = file_age_hours(path)
            if age is not None and age <= MAX_AGE_HOURS:
                recent.add(f)

    if len(recent) < EXPECTED_AGENTS:
        missing = EXPECTED_AGENTS - len(recent)
        write_log(f"⚠️ {missing} agent(s) inactive — attempting restart.")
        for i in range(1, EXPECTED_AGENTS + 1):
            name = f"agent_{i:03d}.py"
            if name not in recent:
                inactive.append(name)
    else:
        write_log(f"✅ All {EXPECTED_AGENTS} agents active.")
    return inactive

def restart_inactive_agents(inactive):
    if not inactive:
        return
    for name in inactive:
        path = os.path.join(AGENT_SCRIPTS_DIR, name)
        if os.path.exists(path):
            write_log(f"🔄 Restarting {name}...")
            run_cmd(f"nohup python3 {path} >/dev/null 2>&1 &")
        else:
            write_log(f"⚠️ Missing agent script: {name}")

# --- MAIN ---
def main():
    write_log("=== Knowledge Sharing Self-Healing Cycle Start ===")
    check_shared_kb()
    inactive = find_inactive_agents()
    restart_inactive_agents(inactive)
    write_log("=== Cycle Complete ===\n")

if __name__ == "__main__":
    main()
