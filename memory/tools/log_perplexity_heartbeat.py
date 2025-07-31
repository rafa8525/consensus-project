#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime
import requests

BASE_DIR = "/home/rafa1215/consensus-project"
AGENTS_LOG_DIR = os.path.join(BASE_DIR, "memory/logs/agents")
os.makedirs(AGENTS_LOG_DIR, exist_ok=True)

def write_log(filename, message):
    log_path = os.path.join(AGENTS_LOG_DIR, filename)
    with open(log_path, "a") as f:
        f.write(f"{datetime.now()} — {message}\n")
    print(f"[{filename}] {message}")

# 1. GitHub Heartbeat
def github_heartbeat():
    try:
        result = subprocess.run(
            ["git", "-C", BASE_DIR, "status"], capture_output=True, text=True
        )
        if result.returncode == 0:
            write_log("github_heartbeat.log", "OK — GitHub accessible")
        else:
            write_log("github_heartbeat.log", "ERROR — GitHub command failed")
    except Exception as e:
        write_log("github_heartbeat.log", f"ERROR — {e}")

# 2. VPN Heartbeat
def vpn_heartbeat():
    try:
        result = subprocess.run(["pgrep", "-f", "openvpn"], capture_output=True)
        if result.returncode == 0:
            write_log("vpn_heartbeat.log", "OK — VPN process running")
        else:
            write_log("vpn_heartbeat.log", "ERROR — VPN not running")
    except Exception as e:
        write_log("vpn_heartbeat.log", f"ERROR — {e}")

# 3. SMS Heartbeat
def sms_heartbeat():
    try:
        sms_log_dir = os.path.join(BASE_DIR, "memory/logs/sms")
        if not os.path.exists(sms_log_dir):
            os.makedirs(sms_log_dir)
        # Check if today's SMS log exists and is non-empty
        today = datetime.now().strftime("%Y-%m-%d")
        found = any(today in f for f in os.listdir(sms_log_dir))
        if found:
            write_log("sms_heartbeat.log", "OK — SMS logs found for today")
        else:
            write_log("sms_heartbeat.log", "WARNING — No SMS logs found for today")
    except Exception as e:
        write_log("sms_heartbeat.log", f"ERROR — {e}")

# 4. Perplexity Heartbeat
def perplexity_heartbeat():
    try:
        # Just a connectivity check — can refine to actual API ping if API key available
        r = requests.get("https://www.perplexity.ai", timeout=5)
        if r.status_code == 200:
            write_log("perplexity_heartbeat.log", "OK — Perplexity reachable")
        else:
            write_log("perplexity_heartbeat.log", f"ERROR — HTTP {r.status_code}")
    except Exception as e:
        write_log("perplexity_heartbeat.log", f"ERROR — {e}")

if __name__ == "__main__":
    print("=== Running Heartbeat Scripts ===")
    github_heartbeat()
    vpn_heartbeat()
    sms_heartbeat()
    perplexity_heartbeat()
    print("=== Heartbeat Scripts Finished ===")
