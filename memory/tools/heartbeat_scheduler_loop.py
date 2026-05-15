#!/usr/bin/env python3
import os
import time
import subprocess
import datetime

# Paths
TOOLS_DIR = "/home/rafa1215/memory/tools"
HEARTBEAT_SCRIPT = os.path.join(TOOLS_DIR, "daily_heartbeat_master.py")
SELF_IMPROVEMENT_SCRIPT = os.path.join(TOOLS_DIR, "agent_self_improvement_master.py")

def run_script(script_path):
    print(f"[RUNNING] {script_path}")
    subprocess.run(["python3", script_path])

def main():
    print("=== Heartbeat Scheduler Loop Started (10 min interval) ===")
    last_self_improvement_run = None

    while True:
        now = datetime.datetime.now()
        today = now.date()

        # Run daily heartbeat checks
        run_script(HEARTBEAT_SCRIPT)

        # Run self-improvement once per day AFTER heartbeat
        if last_self_improvement_run != today:
            run_script(SELF_IMPROVEMENT_SCRIPT)
            last_self_improvement_run = today

        # Wait before next heartbeat cycle
        time.sleep(600)  # 10 minutes

if __name__ == "__main__":
    main()
