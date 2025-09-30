#!/usr/bin/env python3
import os
import subprocess
import time
import datetime
import csv

# === Paths ===
BASE_DIR = "/home/rafa1215/consensus-project/memory"
LOG_DIR = os.path.join(BASE_DIR, "logs/vpn")
LOG_FILE = os.path.join(LOG_DIR, "vpn_log.md")
CSV_FILE = os.path.join(BASE_DIR, "logs/system/agents_assignments.csv")

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)

# === Config ===
PUBLIC_SSIDS = ["BART-WiFi", "MuniFreeWiFi", "StarbucksWiFi", "XfinityWiFi"]

VPN_CONNECT_CMD = ["openvpn", "--config", "/home/rafa1215/consensus-project/config/vpn.ovpn"]
VPN_DISCONNECT_CMD = ["killall", "openvpn"]

# === Logging ===
def log(message: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)
    print(line.strip())

log("=== Starting Unified VPN Runner ===")

# === Step 0: Agent assignment stamping ===
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            log(f"Agent {row['Agent']} responsible for: {row['Responsibility']}")
else:
    log("No agents_assignments.csv found — using default responsibilities.")

# === Helpers ===
def get_current_ssid() -> str:
    try:
        result = subprocess.getoutput("nmcli -t -f active,ssid dev wifi | egrep '^yes' | cut -d':' -f2")
        return result.strip() if result else "UNKNOWN"
    except Exception as e:
        log(f"SSID check failed: {e}")
        return "UNKNOWN"

def vpn_running() -> bool:
    try:
        status = subprocess.getoutput("pgrep openvpn || true")
        return bool(status.strip())
    except Exception:
        return False

def connect_vpn():
    if vpn_running():
        log("VPN already running.")
        return
    try:
        subprocess.Popen(VPN_CONNECT_CMD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
        if vpn_running():
            log("VPN connected successfully.")
        else:
            log("VPN connection attempt failed.")
    except Exception as e:
        log(f"Error during VPN connect: {e}")

def disconnect_vpn():
    if not vpn_running():
        log("VPN not running, nothing to disconnect.")
        return
    try:
        subprocess.call(VPN_DISCONNECT_CMD)
        log("VPN disconnected.")
    except Exception as e:
        log(f"Error during VPN disconnect: {e}")

# === Step 1: Wi-Fi detection + policy enforcement ===
ssid = get_current_ssid()
log(f"Detected SSID: {ssid}")

if ssid in PUBLIC_SSIDS:
    log("Public Wi-Fi detected, ensuring VPN is active.")
    connect_vpn()
else:
    log("Safe network or unknown SSID, ensuring VPN is disconnected.")
    disconnect_vpn()

# === Step 2: VPN process health check ===
if vpn_running():
    log("VPN process confirmed active.")
else:
    log("VPN not active, attempting restart.")
    subprocess.run(["systemctl", "--user", "restart", "openvpn"], check=False)
    time.sleep(3)
    if vpn_running():
        log("VPN restarted successfully.")
    else:
        log("VPN restart failed.")

# === Step 3: Load test ===
try:
    result = subprocess.getoutput("curl -s -o /dev/null -w '%{time_total}' https://www.google.com")
    log(f"Load test response time: {result}s")
except Exception as e:
    log(f"Load test failed: {e}")

# === Step 4: Stress test ===
try:
    result = subprocess.getoutput("ping -c 10 8.8.8.8 | tail -2")
    log(f"Stress test result: {result}")
except Exception as e:
    log(f"Stress test failed: {e}")

# === Step 5: Concurrency test ===
try:
    cmds = ["curl -s -o /dev/null https://www.google.com" for _ in range(3)]
    for cmd in cmds:
        subprocess.Popen(cmd, shell=True)
    log("Concurrency test launched (3 parallel curls).")
except Exception as e:
    log(f"Concurrency test failed: {e}")

# === Step 6: Failover test ===
try:
    log("Running failover test...")
    disconnect_vpn()
    time.sleep(2)
    connect_vpn()
except Exception as e:
    log(f"Failover test failed: {e}")

log("=== Unified VPN Runner Completed ===\n")
