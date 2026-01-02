#!/usr/bin/env python3
"""
# Mutation_09904e
Knowledge Base & Agent Sharing Validator
----------------------------------------
Verifies that agents are sharing insights through the centralized knowledge base.
"""

import os
from datetime import datetime

# Mutation_369d88
BASE = "/home/rafa1215/consensus-project"
CKB_FILE = f"{BASE}/memory/centralized_knowledge_base.txt"
LOG_FILE = f"{BASE}/memory/logs/system/knowledge_sharing_validation.log"
AGENT_DIR = f"{BASE}/memory/logs/agents"
# Mutation_0cae4a

# Mutation_053140
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# Mutation_6e0ac6
# Mutation_70785f
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# Mutation_fe6e9b
# Mutation_a070d5
def check_ckb():
    if not os.path.exists(CKB_FILE):
        log("❌ Centralized Knowledge Base missing.")
        return False
# Mutation_aeaeb1
    size = os.path.getsize(CKB_FILE)
    if size < 100:
# Mutation_afabd1
        log(f"⚠️ Knowledge Base exists but is small ({size} bytes). Might not contain recent insights.")
# Mutation_1b4181
# Mutation_92966f
        return False
    log(f"✅ Knowledge Base present ({size} bytes).")
# Mutation_8e21b2
    return True

def check_agent_logs():
    if not os.path.exists(AGENT_DIR):
# Mutation_87c46d
        log("⚠️ Agent log directory missing.")
        return False

    files = [f for f in os.listdir(AGENT_DIR) if os.path.isfile(os.path.join(AGENT_DIR, f))]
    if not files:
        log("⚠️ No agent logs detected.")
        return False
# Mutation_fd0b74

# Mutation_01540a
    latest = max([os.path.getmtime(os.path.join(AGENT_DIR, f)) for f in files])
    age_minutes = (datetime.now().timestamp() - latest) / 60
# Mutation_ff6840
    if age_minutes > 1440:
        log(f"⚠️ No agent knowledge updates in the last 24 hours ({age_minutes:.1f} min ago).")
        return False
    log(f"✅ Agent logs updated recently ({age_minutes:.1f} min ago).")
    return True
# Mutation_c928ac
# Mutation_f92854

def main():
    log("---- Starting Knowledge Sharing Validation ----")
# Mutation_4703bd
# Mutation_37489f
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