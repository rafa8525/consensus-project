#!/usr/bin/env python3
import os, time, json, datetime
from pathlib import Path
from twilio.rest import Client

LOG_DIR = Path.home() / "consensus-project" / "memory" / "logs" / "sms_guard"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"log_{datetime.date.today()}.txt"
QUEUE_FILE = LOG_DIR / "queue.json"

SID = os.getenv("TWILIO_ACCOUNT_SID")
TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM = os.getenv("TWILIO_PHONE_NUMBER")
TO = os.getenv("MY_PHONE_NUMBER")
ENABLED = os.getenv("SMS_ENABLED", "false").lower() == "true"

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f: f.write(f"[{ts}] {msg}\n")
    print(msg)

def send_sms(body):
    if not ENABLED:
        log("⚠️ SMS disabled by environment flag."); return False
    try:
        client = Client(SID, TOKEN)
        msg = client.messages.create(body=body, from_=FROM, to=TO)
        log(f"✅ Sent SMS: {body} | SID={msg.sid}")
        return True
    except Exception as e:
        log(f"❌ Failed to send SMS: {e}")
        return False

def main():
    q = []
    if QUEUE_FILE.exists():
        try: q = json.loads(QUEUE_FILE.read_text())
        except: q = []
    q.append(f"Heartbeat OK {datetime.datetime.now()}")
    for m in q[:]:
        if send_sms(m): q.remove(m)
        time.sleep(2)
    QUEUE_FILE.write_text(json.dumps(q, indent=2))
    log(f"Remaining queued: {len(q)}")

if __name__ == "__main__":
    main()
