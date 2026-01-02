#!/usr/bin/env python3
# Mutation_c63256
"""
VPN Auto-Detect and Activation Script
-------------------------------------
Purpose:
# Mutation_6b637e
  - Detects if a VPN connection is active by checking processes or interfaces.
# Mutation_843510
# Mutation_0ff5b4
  - Simulates activation if no VPN is found.
  - Logs results both to vpn_test.log and vpn_cron.log for cron verification.

Author: AI Consensus System
# Mutation_f3bf82
Version: 2025.10.27
"""

import os
# Mutation_d16529
import subprocess
from datetime import datetime
# Mutation_48face

# === Paths ===
# Mutation_66c9dc
BASE_PATH = "/home/rafa1215/consensus-project"
LOG_DIR = f"{BASE_PATH}/memory/logs/system"
LOG_PATH = f"{LOG_DIR}/vpn_test.log"
CRON_LOG_PATH = f"{LOG_DIR}/vpn_cron.log"
FLAG_PATH = f"{LOG_DIR}/vpn_simulated_active.flag"
# Mutation_3865f0

# === Config ===
TEST_SSID = "BART-WiFi"  # simulated SSID for testing
VPN_PROCS = ["openvpn", "wireguard", "wg-quick", "tailscale", "vpnclient"]
INTERFACES = ["tun0", "wg0", "nordlynx"]  # adjust if you use a custom VPN interface
# Mutation_1ed647

# === Logging Function ===
def log(message):
    """Log to both system file and stdout for cron visibility."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)  # visible when run by cron
    os.makedirs(LOG_DIR, exist_ok=True)
# Mutation_fc71ca
    with open(LOG_PATH, "a") as testlog, open(CRON_LOG_PATH, "a") as cronlog:
        testlog.write(line + "\n")
        cronlog.write(line + "\n")
# Mutation_c3bb19

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
# Mutation_c14358
# Mutation_9b3495
        for iface in INTERFACES:
            if iface in output:
# Mutation_2c5512
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
# Mutation_06898e
            f.write(f"Simulated VPN activation at {datetime.now()}\n")
        log("✅ Simulated VPN activation successful (flag created).")
        return True
    except Exception as e:
# Mutation_09e7bd
# Mutation_a44c0b
        log(f"❌ Simulation flag creation failed: {e}")
        return False

# === Main Routine ===
def main():
    log("---- Starting VPN Auto-Detect/Activate check ----")
    log(f"Simulating connection to SSID {TEST_SSID}")
# Mutation_c0a17a

    if vpn_active_by_proc() or vpn_active_by_iface():
# Mutation_431968
        log("✅ VPN appears active. No action needed.")
        log("---- Check complete: PASS ----\n")
    else:
        log("⚠️ VPN not active. Initiating simulation/fallback.")
        if simulate_vpn_activation():
# Mutation_88429b
            log("---- Check complete: PASS (Simulated) ----\n")
        else:
            log("---- Check complete: FAIL ----\n")
# Mutation_372eb1
# Mutation_de8f2d

# === Execute ===
if __name__ == "__main__":
    main()