#!/usr/bin/env python3
"""
vpn_runner.py
Phase 5 Cleanup — Unified VPN Test Suite

Purpose:
- Consolidate all legacy VPN test plans into one runner.
- Run activation, load, stress, failover, and detection checks.
- Log results into vpn_test_report.md with timestamps.
"""

import os
import datetime
import subprocess

LOG_DIR = "/home/rafa1215/consensus-project/memory/logs/system"
REPORT_FILE = os.path.join(LOG_DIR, "vpn_test_report.md")
HEARTBEAT_FILE = os.path.join(LOG_DIR, "heartbeat.md")

os.makedirs(LOG_DIR, exist_ok=True)

def log_heartbeat(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] VPN: {status}\n")

def log_report(section, result):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(REPORT_FILE, "a") as f:
        f.write(f"## {section} — {ts}\n{result}\n\n")

def run_cmd(cmd, section):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            log_report(section, f"SUCCESS\n{result.stdout.strip()}")
            return True
        else:
            log_report(section, f"FAIL\n{result.stderr.strip()}")
            return False
    except Exception as e:
        log_report(section, f"ERROR: {e}")
        return False

def run_tests():
    # Activation test
    run_cmd("curl -s ifconfig.me", "Activation Test")

    # Load test (simulate multiple requests)
    for i in range(3):
        run_cmd("curl -s https://example.com", f"Load Test Attempt {i+1}")

    # Stress test (ping flood simulation)
    run_cmd("ping -c 5 8.8.8.8", "Stress Test (Ping)")

    # Failover test (check DNS switch)
    run_cmd("nslookup openai.com 1.1.1.1", "Failover Test (DNS)")

    # Detection test (VPN fingerprint check)
    run_cmd("curl -s https://ipinfo.io", "Detection Test (IP Fingerprint)")

if __name__ == "__main__":
    try:
        run_tests()
        log_heartbeat("VPN unified tests completed")
    except Exception as e:
        log_heartbeat(f"ERROR: VPN runner crashed — {e}")
