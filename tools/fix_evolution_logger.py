#!/usr/bin/env python3
"""
fix_evolution_logger.py
Repairs and reboots the AI Evolution Cycle logging system on PythonAnywhere.
Safe to run multiple times (idempotent).
"""

import os
import stat
import time
import subprocess

BASE = os.path.expanduser("~/consensus-project")
LOG_DIR = os.path.join(BASE, "memory/logs/system")
LOG_PATH = os.path.join(LOG_DIR, "ai_evolution_cycle.log")
SCRIPT_PATH = os.path.join(BASE, "tools/ai_evolution_cycle.py")
SCHED_PATH = os.path.join(BASE, "schedule_utc.txt")

def ensure_permissions(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        os.chmod(path, 0o777)
    except Exception as e:
        print(f"[WARN] Could not chmod {path}: {e}")

def ensure_log_file():
    ensure_permissions(LOG_DIR)
    if not os.path.exists(LOG_PATH):
        open(LOG_PATH, "a").close()
    os.chmod(LOG_PATH, 0o666)
    print(f"[OK] Log file ready at {LOG_PATH}")

def test_write_log():
    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] 🧠 Fix script executed — verifying log integrity...\n")
        f.flush(); os.fsync(f.fileno())
    print("[OK] Test line written to log.")

def verify_schedule_entry():
    """Ensure evolution script is scheduled daily."""
    if not os.path.exists(SCHED_PATH):
        print("[INFO] schedule_utc.txt not found — creating new one.")
        open(SCHED_PATH, "a").close()

    with open(SCHED_PATH, "r+", encoding="utf-8") as f:
        lines = f.read().splitlines()
        pattern = "ai_evolution_cycle.py"
        if not any(pattern in line for line in lines):
            f.write("\n# Auto-added by fix_evolution_logger\n")
            f.write("0 * * * * python3 ~/consensus-project/tools/ai_evolution_cycle.py >> ~/memory/logs/system/ai_evolution_cycle.log 2>&1\n")
            print("[OK] Evolution cycle scheduled hourly.")
        else:
            print("[OK] Schedule entry already exists.")

def run_one_cycle():
    if not os.path.exists(SCRIPT_PATH):
        print(f"[ERROR] {SCRIPT_PATH} missing — cannot run evolution test.")
        return
    print("[RUN] Executing one manual evolution cycle...")
    try:
        subprocess.run(
            ["python3", SCRIPT_PATH],
            cwd=os.path.dirname(SCRIPT_PATH),
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception as e:
        print(f"[ERROR] Failed to run evolution cycle: {e}")
    time.sleep(2)
    print("[CHECK] Last few log lines:")
    os.system(f"tail -n 5 {LOG_PATH}")

def main():
    print("=== Fix Evolution Logger: Start ===")
    ensure_log_file()
    test_write_log()
    verify_schedule_entry()
    run_one_cycle()
    print("=== Fix Evolution Logger: Complete ===")

if __name__ == "__main__":
    main()
