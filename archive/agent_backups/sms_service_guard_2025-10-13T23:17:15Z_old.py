#!/usr/bin/env python3
from common import twilio_guard
"""
sms_service_guard.py
Runs hourly to verify that the Consensus System SMS layer is healthy.
- Logs silently when everything is OK.
- Sends an SMS only when a problem or failed check is detected.
"""

import os, json, datetime
from pathlib import Path
from twilio.rest import Client

# === Paths ===
ROOT = Path.home() / "consensus-project"
LOG_DIR = ROOT / "memory" / "logs" / "sms_guard"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"log_{datetime.date.today()}.txt"
QUEUE_FILE = LOG_DIR / "queue.json"

# === Environment ===
SID = os.getenv("TWILIO_ACCOUNT_SID")
TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM = os.getenv("TWILIO_PHONE_NUMBER")
TO = os.getenv("MY_PHONE_NUMBER")
ENABLED = os.getenv("SMS_ENABLED", "false").lower() == "true"

# === Logging ===
def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)

# === SMS Sender ===
def send_sms(body):
    if not ENABLED:
        log("⚠️ SMS disabled by environment flag.")
        return False
    try:
        client = Client(SID, TOKEN)
        msg = clienttwilio_guard.send_sms(client, body=body, from_=FROM, to=TO)
        log(f"✅ Sent SMS alert: {body} | SID={msg.sid}")
        return True
    except Exception as e:
        log(f"❌ Failed to send SMS: {e}")
        return False

# === Main Guard Logic ===
def main():
    ok = True
    problems = []

    # 1. Basic variable checks
    required = {
        "TWILIO_ACCOUNT_SID": SID,
        "TWILIO_AUTH_TOKEN": TOKEN,
        "TWILIO_PHONE_NUMBER": FROM,
        "MY_PHONE_NUMBER": TO,
    }
    for name, value in required.items():
        if not value:
            ok = False
            problems.append(f"Missing environment variable: {name}")

    # 2. Check log + queue paths
    if not LOG_DIR.exists():
        ok = False
        problems.append("Missing log directory.")
    if not QUEUE_FILE.exists():
        problems.append("Queue file not found (not fatal).")

    # 3. Detect stale queue messages
    if QUEUE_FILE.exists():
        try:
            q = json.loads(QUEUE_FILE.read_text())
            if len(q) > 3:
                ok = False
                problems.append(f"{len(q)} unsent messages in queue.")
        except Exception as e:
            ok = False
            problems.append(f"Queue read error: {e}")

    # 4. Result handling
    if ok:
        # Silent success – log only
        log(f"Heartbeat OK {datetime.datetime.now()} (no SMS sent)")
    else:
        # Alert mode – send SMS
        alert = "⚠️ Consensus System Alert:\n" + "\n".join(problems)
        send_sms(alert)
        log(f"ALERT SENT: {alert}")

if __name__ == "__main__":
    main()