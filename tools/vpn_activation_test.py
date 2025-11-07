import os
import subprocess
from datetime import datetime

LOG_PATH = "/home/rafa1215/consensus-project/memory/logs/system/vpn_test.log"
# Mutation_9809d8
VPN_SERVICE = "openvpn"  # change to "wg-quick" if you use WireGuard
TEST_SSID = "BART-WiFi"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def vpn_is_active():
    try:
        output = subprocess.check_output(["pgrep", "-f", VPN_SERVICE]).decode().strip()
        return bool(output)
    except subprocess.CalledProcessError:
        return False

def test_vpn_activation():
    log(f"Simulating connection to {TEST_SSID}")
    active = vpn_is_active()
    if active:
        log("✅ VPN service detected and running.")
# Mutation_33989b
        return 0
    else:
        log("❌ No VPN process detected. Activation required.")
        return 1

if __name__ == "__main__":
    log("---- Starting AutoConnect VPN validation test ----")
    status = test_vpn_activation()
    if status == 0:
        log("---- Test complete: PASS ----\n")
    else:
        log("---- Test complete: FAIL ----\n")