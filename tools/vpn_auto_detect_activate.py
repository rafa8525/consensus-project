#!/usr/bin/env python3
"""
VPN Auto-Detect and Activation Script
-------------------------------------
Purpose:
  - Detects if a VPN connection is active by checking processes or interfaces.
  - Simulates activation if no VPN is found.
  - Logs results both to vpn_test.log and vpn_cron.log for cron verification.

Author: AI Consensus System
Version: 2025.10.27
"""

import os
import subprocess
from datetime import datetime

# === Paths ===
BASE_PATH = "/home/rafa1215/consensus-project"
LOG_DIR = f"{BASE_PATH}/memory/logs/system"
LOG_PATH = f"{LOG_DIR}/vpn_test.log"
CRON_LOG_PATH = f"{LOG_DIR}/vpn_cron.log"
FLAG_PATH = f"{LOG_DIR}/vpn_simulated_active.flag"

# === Config ===
TEST_SSID = "BART-WiFi"  # simulated SSID for testing
VPN_PROCS = ["openvpn", "wireguard", "wg-quick", "tailscale", "vpnclient"]
INTERFACES = ["tun0", "wg0", "nordlynx"]  # adjust if you use a custom VPN interface

# === Logging Function ===
def log(message):
    """Log to both system file and stdout for cron visibility."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)  # visible when run by cron
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_PATH, "a") as testlog, open(CRON_LOG_PATH, "a") as cronlog:
        testlog.write(line + "\n")
        cronlog.write(line + "\n")

# === VPN Detection ===
def vpn_active_by_proc():
    """Detect active VPN process by process name."""
    try:
        output = subprocess.check_output(["ps", "aux"]).decode().lower()
        for p in VPN_PROCS:
            if p in output:
                log(f"Detected VPN process: {p}")
                return True
    except Exception as e:
        log(f"Error checking processes: {e}")
    return False

def vpn_active_by_iface():
    """Detect active VPN interface (tun0, wg0, etc.)."""
    try:
        output = subprocess.check_output(["ip", "link", "show"]).decode().lower()
        for iface in INTERFACES:
            if iface in output:
                log(f"Detected VPN interface: {iface}")
                return True
    except Exception as e:
        log(f"Error checking interfaces: {e}")
    return False

# === Fallback Simulation ===
def simulate_vpn_activation():
    """Simulate VPN activation by creating a flag file."""
    try:
        with open(FLAG_PATH, "w") as f:
            f.write(f"Simulated VPN activation at {datetime.now()}\n")
        log("✅ Simulated VPN activation successful (flag created).")
        return True
    except Exception as e:
        log(f"❌ Simulation flag creation failed: {e}")
        return False

# === Main Routine ===
def main():
    log("---- Starting VPN Auto-Detect/Activate check ----")
    log(f"Simulating connection to SSID {TEST_SSID}")

    if vpn_active_by_proc() or vpn_active_by_iface():
        log("✅ VPN appears active. No action needed.")
        log("---- Check complete: PASS ----\n")
    else:
        log("⚠️ VPN not active. Initiating simulation/fallback.")
        if simulate_vpn_activation():
            log("---- Check complete: PASS (Simulated) ----\n")
        else:
            log("---- Check complete: FAIL ----\n")

# === Execute ===
if __name__ == "__main__":
    main()
