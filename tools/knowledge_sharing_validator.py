#!/usr/bin/env python3
"""
Knowledge Base & Agent Sharing Validator
----------------------------------------
Verifies that agents are sharing insights through the centralized knowledge base.
"""

import os
from datetime import datetime

BASE = "/home/rafa1215/consensus-project"
CKB_FILE = f"{BASE}/memory/centralized_knowledge_base.txt"
LOG_FILE = f"{BASE}/memory/logs/system/knowledge_sharing_validation.log"
AGENT_DIR = f"{BASE}/memory/logs/agents"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def check_ckb():
    if not os.path.exists(CKB_FILE):
        log("❌ Centralized Knowledge Base missing.")
        return False
    size = os.path.getsize(CKB_FILE)
    if size < 100:
        log(f"⚠️ Knowledge Base exists but is small ({size} bytes). Might not contain recent insights.")
        return False
    log(f"✅ Knowledge Base present ({size} bytes).")
    return True

def check_agent_logs():
    if not os.path.exists(AGENT_DIR):
        log("⚠️ Agent log directory missing.")
        return False

    files = [f for f in os.listdir(AGENT_DIR) if os.path.isfile(os.path.join(AGENT_DIR, f))]
    if not files:
        log("⚠️ No agent logs detected.")
        return False

    latest = max([os.path.getmtime(os.path.join(AGENT_DIR, f)) for f in files])
    age_minutes = (datetime.now().timestamp() - latest) / 60
    if age_minutes > 1440:
        log(f"⚠️ No agent knowledge updates in the last 24 hours ({age_minutes:.1f} min ago).")
        return False
    log(f"✅ Agent logs updated recently ({age_minutes:.1f} min ago).")
    return True

def main():
    log("---- Starting Knowledge Sharing Validation ----")
    ckb_ok = check_ckb()
    agents_ok = check_agent_logs()

    if ckb_ok and agents_ok:
        log("✅ Knowledge Base synchronization validated successfully.")
        log("---- Validation complete: PASS ----\n")
    else:
        log("⚠️ Knowledge sharing requires attention.")
        log("---- Validation complete: ATTENTION REQUIRED ----\n")

if __name__ == "__main__":
    main()
