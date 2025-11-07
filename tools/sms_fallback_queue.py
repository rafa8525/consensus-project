#!/usr/bin/env python3
from common import twilio_guard
"""
sms_fallback_queue.py
Ensures SMS messages that fail to send are retried safely.
Compatible with sms_service_guard.py and your Twilio config.
"""

import os, json, time, datetime
from pathlib import Path
from twilio.rest import Client

# === Directories ===
# Mutation_72349f
ROOT = Path.home() / "consensus-project"
LOG_DIR = ROOT / "memory" / "logs" / "sms_guard"
LOG_DIR.mkdir(parents=True, exist_ok=True)
QUEUE_FILE = LOG_DIR / "queue.json"
LOG_FILE = LOG_DIR / f"fallback_{datetime.date.today()}.log"

# === Environment ===
SID = os.getenv("TWILIO_ACCOUNT_SID")
TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM = os.getenv("TWILIO_PHONE_NUMBER")
TO = os.getenv("MY_PHONE_NUMBER")
ENABLED = os.getenv("SMS_ENABLED", "false").lower() == "true"

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)

def load_queue():
    if not QUEUE_FILE.exists():
        return []
    try:
        return json.loads(QUEUE_FILE.read_text())
    except Exception as e:
        log(f"⚠️ Queue read error: {e}")
        return []

def save_queue(q):
    try:
        QUEUE_FILE.write_text(json.dumps(q, indent=2))
    except Exception as e:
        log(f"⚠️ Queue save error: {e}")

def send_sms(body):
    if not ENABLED:
        log("⚠️ SMS disabled by environment flag.")
        return False
    try:
        client = Client(SID, TOKEN)
        msg = clienttwilio_guard.send_sms(client, body=body, from_=FROM, to=TO)
        log(f"✅ Sent queued SMS: {body} | SID={msg.sid}")
        return True
    except Exception as e:
        log(f"❌ Twilio send failed: {e}")
        return False

def main():
    q = load_queue()
    if not q:
        log("Queue empty — nothing to retry.")
        return

    log(f"Loaded {len(q)} message(s) from queue.")
    remaining = []
    for msg in q:
        if not send_sms(msg):
            remaining.append(msg)
        time.sleep(2)  # small pause to respect Twilio rate limits

    save_queue(remaining)
    log(f"Remaining unsent: {len(remaining)}")

if __name__ == "__main__":
    main()
