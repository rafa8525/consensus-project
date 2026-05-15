#!/usr/bin/env python3
import os
import time
import subprocess
from datetime import datetime

# Paths
PROJECT_ROOT = "/home/rafa1215/consensus-project"
MEMORY_ROOT = os.path.join(PROJECT_ROOT, "memory")
HEARTBEAT_LOG = os.path.join(MEMORY_ROOT, "logs/heartbeat/memory_absorption_heartbeat.log")
FULL_LOG = os.path.join(MEMORY_ROOT, "logs/heartbeat/full_memory_absorption.log")

# Text file types to fully absorb
TEXT_FILE_EXTENSIONS = [".txt", ".md", ".log", ".json", ".csv", ".py", ".yml", ".yaml"]

# Existing heartbeat scripts
OTHER_HEARTBEATS = [
    os.path.join(MEMORY_ROOT, "tools/log_vpn_heartbeat.py"),
    os.path.join(MEMORY_ROOT, "tools/log_github_heartbeat.py"),
    os.path.join(MEMORY_ROOT, "tools/log_sms_heartbeat.py"),
    # Add any others you want here
]

def should_absorb(file_path):
    """Return True if file should be absorbed word-for-word."""
    return any(file_path.lower().endswith(ext) for ext in TEXT_FILE_EXTENSIONS)

def absorb_memory():
    """Recursively absorb all memory files word-for-word."""
    absorbed_data = []
    for root, dirs, files in os.walk(MEMORY_ROOT):
        for file in files:
            file_path = os.path.join(root, file)
            if should_absorb(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    absorbed_data.append(f"\n--- FILE: {file_path} ---\n{content}")
                except Exception as e:
                    absorbed_data.append(f"\n--- FILE: {file_path} ---\n[ERROR READING FILE: {e}]")
    return "\n".join(absorbed_data)

def write_memory_absorption():
    """Write full memory absorption + heartbeat log."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Heartbeat
    with open(HEARTBEAT_LOG, "w", encoding="utf-8") as hb:
        hb.write(f"Last full memory absorption: {now}\n")
    # Full absorption log
    all_memory = absorb_memory()
    with open(FULL_LOG, "w", encoding="utf-8") as fm:
        fm.write(f"=== Full Memory Absorption Log ===\nGenerated: {now}\n")
        fm.write(all_memory)
    print(f"[{now}] Memory absorption complete.")

def git_commit_and_push():
    """Push updated logs to GitHub."""
    try:
        subprocess.run(
            ["git", "-C", PROJECT_ROOT, "add", "memory/logs/heartbeat/"],
            check=True
        )
        subprocess.run(
            ["git", "-C", PROJECT_ROOT, "commit", "-m", "[AUTO] Memory full absorption + heartbeats update"],
            check=False
        )
        subprocess.run(
            ["git", "-C", PROJECT_ROOT, "push"],
            check=True
        )
        print(f"[{datetime.now()}] Git push complete.")
    except Exception as e:
        print(f"[ERROR] Git push failed: {e}")

def run_other_heartbeats():
    """Run your other existing heartbeat scripts."""
    for script in OTHER_HEARTBEATS:
        if os.path.exists(script):
            print(f"[{datetime.now()}] Running: {script}")
            subprocess.run(["/usr/bin/python3", script], check=False)

def master_loop():
    """Run all heartbeats + full memory absorption in a loop forever."""
    while True:
        print(f"[{datetime.now()}] ===== Starting master heartbeat cycle =====")
        write_memory_absorption()
        run_other_heartbeats()
        git_commit_and_push()
        print(f"[{datetime.now()}] ===== Cycle complete. Sleeping... =====")
        time.sleep(1800)  # 30 minutes

if __name__ == "__main__":
    master_loop()
