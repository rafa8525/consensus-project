#!/usr/bin/env python3
import os
import datetime
import subprocess

BASE_DIR = "/home/rafa1215/consensus-project/memory"
LOG_DIR = os.path.join(BASE_DIR, "logs/notifications")
HEARTBEAT_FILE = os.path.join(BASE_DIR, "logs/system/heartbeat.md")

os.makedirs(LOG_DIR, exist_ok=True)

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(level: str, message: str):
    ts = now()
    entry = f"[{ts}] {level}: {message}\n"
    # Heartbeat
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] NOTIFY: {level}: {message}\n")
    # Push log
    with open(os.path.join(LOG_DIR, "push_log.md"), "a") as f:
        f.write(entry)
    print(entry.strip())

def send_sms(message: str):
    if os.environ.get("SMS_ENABLED", "false").lower() == "true":
        try:
            subprocess.run(
                ["python3", "/home/rafa1215/consensus-project/tools/send_sms_alert.py", message],
                check=False
            )
        except Exception as e:
            log("ERROR", f"SMS send failed: {e}")

def notify(level: str, message: str):
    level = level.upper()
    if level == "INFO":
        log("INFO", message)
    elif level == "WARNING":
        log("WARNING", message)
    elif level == "CRITICAL":
        log("CRITICAL", message)
        send_sms(message)
    else:
        log("INFO", f"(unrecognized level {level}) {message}")

if __name__ == "__main__":
    # Example demo
    notify("INFO", "Heartbeat normal")
    notify("WARNING", "VPN latency high")
    notify("CRITICAL", "Absorb pipeline failed after retries")
