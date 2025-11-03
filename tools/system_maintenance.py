#!/usr/bin/python3
import os, subprocess, datetime

TOOLS = "/home/rafa1215/consensus-project/tools"
LOGS  = "/home/rafa1215/memory/logs/system/system_maintenance.log"

def safe_run(script):
    path = os.path.join(TOOLS, script)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOGS, "a") as log:
        if not os.path.exists(path):
            log.write(f"[{ts}] ⚠️ {script} missing — skipping.\n")
            print(f"⚠️ {script} missing — skipping.")
            return
        log.write(f"[{ts}] 🔄 {script}...\n"); print(f"🔄 {script}...")
        try:
            subprocess.run(["python3", path], check=True)
            log.write(f"[{ts}] ✅ {script} OK\n")
        except subprocess.CalledProcessError as e:
            log.write(f"[{ts}] ❌ {script} failed: {e}\n")
            print(f"❌ {script} failed: {e}")

if __name__ == "__main__":
    sequence = [
        "overnight_guard.py",
        "agent_sweep.py",
        "log_rotate.py",
        "log_memory_manifest.py",
        "integration_manifest.py",
    ]
    for s in sequence:
        safe_run(s)
    print("✅ System maintenance sequence finished without fatal errors.")
