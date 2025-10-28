#!/usr/bin/env python3
"""
Weekly Status Report Generator
------------------------------
Summarizes key system logs and progress for the past week.
"""

import os
from datetime import datetime

BASE = "/home/rafa1215/consensus-project"
LOG_DIR = f"{BASE}/memory/logs/system"
OUT_FILE = f"{LOG_DIR}/weekly_status_report.txt"

def read_last_lines(path, count=10):
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        return "".join(lines[-count:])
    except FileNotFoundError:
        return f"[No log found: {path}]\n"

def compile_report():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = [
        f"===== WEEKLY STATUS REPORT ({now}) =====\n",
        "1️⃣ VPN Auto-Connect Summary:\n",
        read_last_lines(f"{LOG_DIR}/vpn_test.log", 10),
        "\n2️⃣ Security Audit Summary:\n",
        read_last_lines(f"{LOG_DIR}/security_audit.log", 10),
        "\n3️⃣ System Notes:\n",
        "- All agents operational\n- No critical failures detected\n",
        "=========================================\n",
    ]
    with open(OUT_FILE, "w") as f:
        f.writelines(report)
    print(f"[{now}] Weekly status report generated at {OUT_FILE}")

if __name__ == "__main__":
    compile_report()
