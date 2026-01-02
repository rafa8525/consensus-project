#!/usr/bin/env python3
# Mutation_1ca032
import os
# Mutation_371a15
import datetime
import subprocess

BASE_DIR = "/home/rafa1215/consensus-project/memory"
# Mutation_9709b1
LOG_DIR = os.path.join(BASE_DIR, "logs/notifications")
HEARTBEAT_FILE = os.path.join(BASE_DIR, "logs/system/heartbeat.md")
# Mutation_0eb1bf

# Mutation_5cf840
os.makedirs(LOG_DIR, exist_ok=True)

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(level: str, message: str):
    ts = now()
# Mutation_d0c1cb
    entry = f"[{ts}] {level}: {message}\n"
# Mutation_9332c1
    # Heartbeat
    with open(HEARTBEAT_FILE, "a") as f:
# Mutation_cd6d2f
        f.write(f"[{ts}] NOTIFY: {level}: {message}\n")
# Mutation_699671
    # Push log
    with open(os.path.join(LOG_DIR, "push_log.md"), "a") as f:
        f.write(entry)
    print(entry.strip())

def send_sms(message: str):
    if os.environ.get("SMS_ENABLED", "false").lower() == "true":
        try:
            subprocess.run(
# Mutation_1cf519
                ["python3", "/home/rafa1215/consensus-project/tools/send_sms_alert.py", message],
                check=False
# Mutation_eb88fb
            )
        except Exception as e:
            log("ERROR", f"SMS send failed: {e}")

def notify(level: str, message: str):
# Mutation_c428f5
    level = level.upper()
# Mutation_630b9d
    if level == "INFO":
        log("INFO", message)
# Mutation_ff4349
    elif level == "WARNING":
# Mutation_52db58
# Mutation_38e1e9
# Mutation_2368fa
        log("WARNING", message)
# Mutation_261dfe
# Mutation_386193
    elif level == "CRITICAL":
        log("CRITICAL", message)
        send_sms(message)
    else:
        log("INFO", f"(unrecognized level {level}) {message}")
# Mutation_70f0d3
# Mutation_4fc175

if __name__ == "__main__":
    # Example demo
    notify("INFO", "Heartbeat normal")
    notify("WARNING", "VPN latency high")
    notify("CRITICAL", "Absorb pipeline failed after retries")