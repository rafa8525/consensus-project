#!/usr/bin/env python3
"""
security_reliability.py
Phase 5 Step 5: Advanced Security & Reliability

Purpose:
- Manage credential vaulting (encrypted secrets).
- Auto-heal failed tasks by monitoring heartbeat logs.
"""

import os
import json
import datetime
import subprocess
from pathlib import Path
from cryptography.fernet import Fernet

BASE = Path("/home/rafa1215/consensus-project")
LOG_DIR = BASE / "memory/logs/security"
HEARTBEAT_FILE = BASE / "memory/logs/system/heartbeat.md"
VAULT_FILE = BASE / "memory/config/credential_vault.json"
KEY_FILE = BASE / "memory/config/vault.key"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(VAULT_FILE.parent, exist_ok=True)

# ====== Credential Vault ======
def init_key():
    if not KEY_FILE.exists():
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)

def load_cipher():
    return Fernet(KEY_FILE.read_bytes())

def vault_store(label, secret):
    cipher = load_cipher()
    data = {}
    if VAULT_FILE.exists():
        data = json.loads(VAULT_FILE.read_text())
    data[label] = cipher.encrypt(secret.encode()).decode()
    VAULT_FILE.write_text(json.dumps(data, indent=2))

def vault_retrieve(label):
    if not VAULT_FILE.exists():
        return None
    data = json.loads(VAULT_FILE.read_text())
    cipher = load_cipher()
    if label in data:
        return cipher.decrypt(data[label].encode()).decode()
    return None

# ====== Auto-Healing Watchdog ======
def check_failures():
    if not HEARTBEAT_FILE.exists():
        return []
    lines = HEARTBEAT_FILE.read_text().splitlines()[-200:]
    failures = {}
    for line in lines:
        if "ERROR" in line or "failed" in line.lower():
            parts = line.split()
            if len(parts) > 2:
                task = parts[2]
                failures[task] = failures.get(task, 0) + 1
    return [task for task, count in failures.items() if count >= 2]

def restart_task(task_name):
    try:
        subprocess.run(
            ["pkill", "-f", task_name],
            check=False
        )
        subprocess.run(
            ["/usr/bin/python3", str(BASE / "tools" / task_name)],
            check=False
        )
        log_heartbeat(f"Auto-healed task: {task_name}")
    except Exception as e:
        log_heartbeat(f"ERROR auto-healing {task_name}: {e}")

# ====== Logging ======
def log_heartbeat(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] SECURITY-REL: {status}\n")

# ====== Main ======
def run_security_reliability():
    init_key()

    # Scan for repeated failures
    bad_tasks = check_failures()
    if bad_tasks:
        for t in bad_tasks:
            restart_task(t)
    else:
        log_heartbeat("No tasks required auto-healing")

if __name__ == "__main__":
    try:
        run_security_reliability()
    except Exception as e:
        log_heartbeat(f"ERROR: Security & Reliability crashed — {e}")
