import datetime
from pathlib import Path

#  Define public SSIDs that should trigger VPN
PUBLIC_SSIDS = ["BART-WiFi", "MuniFreeWiFi", "XfinityWiFi", "Starbucks"]

# 🔧 Mocked current Wi-Fi SSID (replace this later with dynamic detection if needed)
CURRENT_SSID = "BART-WiFi"  # Example match; change for testing

#  Log file path
LOG_FILE = Path("vpn_activation_log.txt")

def log_activation(ssid, status):
    log_entry = f"{datetime.datetime.now().isoformat()} — SSID: {ssid} — VPN: {status}\n"
    with LOG_FILE.open("a") as f:
        f.write(log_entry)

def main():
    if CURRENT_SSID in PUBLIC_SSIDS:
        log_activation(CURRENT_SSID, "ACTIVATED")
        #  VPN trigger would go here (e.g., os.system("nordvpn connect"))
    else:
        log_activation(CURRENT_SSID, "SKIPPED")

if __name__ == "__main__":
    main()
