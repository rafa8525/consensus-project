#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
daily_heartbeat_master.py
Runs all heartbeat logging scripts for AI Consensus System.
Updated to include calendar logging every cycle.
"""

import os
import subprocess
import datetime

TOOLS_DIR = "/home/rafa1215/consensus-project/memory/tools"

# List of heartbeat scripts to run
HEARTBEAT_SCRIPTS = [
    "log_github_heartbeat.py",
    "log_vpn_heartbeat.py",
    "log_sms_heartbeat.py",
    "log_perplexity_heartbeat.py",
    "log_calendar_heartbeat.py"  # NEW
]

print(f"=== Daily Heartbeat Master Run Started {datetime.datetime.now()} ===")
for script in HEARTBEAT_SCRIPTS:
    script_path = os.path.join(TOOLS_DIR, script)
    if os.path.exists(script_path):
        print(f"[RUNNING] {script}")
        try:
            subprocess.run(["python3", script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] {script} failed → {e}")
    else:
        print(f"[MISSING] {script}")

print(f"=== Daily Heartbeat Master Run Finished {datetime.datetime.now()} ===")
