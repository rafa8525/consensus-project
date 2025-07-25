import os
from datetime import datetime

# Paths
LOG_FILE = os.path.expanduser("~/consensus-project/memory/logs/geofencing/kitchen_log.md")
SSID_FILE = os.path.expanduser("~/consensus-project/memory/state/current_ssid.txt")  # Simulated input

# Constants
TARGET_SSID = "PixelWatch-Kitchen"

def get_current_time():
    return datetime.now().strftime("%I:%M %p")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def read_ssid():
    if os.path.exists(SSID_FILE):
        with open(SSID_FILE, "r") as f:
            return f.read().strip()
    return None

def ensure_log_header():
    today = get_current_date()
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write(f"## {today}\n")
    else:
        with open(LOG_FILE, "r") as f:
            content = f.read()
        if f"## {today}" not in content:
            with open(LOG_FILE, "a") as f:
                f.write(f"\n## {today}\n")

def log_entry():
    ensure_log_header()
    now = get_current_time()
    with open(LOG_FILE, "a") as f:
        f.write(f"- Entered Kitchen: {now}\n")
        f.write(f"  - Detected SSID: {TARGET_SSID}\n")
        f.write(f"  - Triggered: fridge_scan.md\n")

if __name__ == "__main__":
    current_ssid = read_ssid()
    if current_ssid == TARGET_SSID:
        log_entry()
