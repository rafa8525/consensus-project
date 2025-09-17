#!/usr/bin/env python3
# sms_sandbox_monitor.py
# Purpose: Safe, low-frequency SMS test harness for Twilio
# - Sends at most 1 SMS per run
# - Only runs between 08:00 and 21:00 local time
# - Logs API responses for analysis
# - No retries, no floods, no calls

import os
import json
import datetime
from pathlib import Path
from twilio.rest import Client

# ===== CONFIG =====
TO_NUMBER = "+16502283267"   # Rafael’s number
FROM_NUMBER = "+18886607830" # Twilio number you confirmed
LOG_DIR = Path("/home/rafa1215/consensus-project/memory/logs/system")
LOG_FILE = LOG_DIR / "sms_sandbox_log.json"

# Load Twilio creds from environment
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def load_log():
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_log(entries):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(json.dumps(entries, indent=2), encoding="utf-8")

def within_active_hours():
    """Only send between 08:00 and 21:00 local time (PDT)."""
    now = datetime.datetime.now()
    return 8 <= now.hour < 21

def main():
    if not within_active_hours():
        print(f"[{now_iso()}] Skipping SMS (outside quiet hours).")
        return

    if not ACCOUNT_SID or not AUTH_TOKEN:
        print(f"[{now_iso()}] Missing Twilio credentials in environment.")
        return

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    try:
        msg = client.messages.create(
            to=TO_NUMBER,
            from_=FROM_NUMBER,
            body=f"[Sandbox Test] Hello Rafael — {now_iso()}",
        )
        status = {
            "time": now_iso(),
            "sid": msg.sid,
            "status": msg.status,
            "to": TO_NUMBER,
            "from": FROM_NUMBER,
        }
        print(f"[{now_iso()}] SMS attempt result: {status}")
    except Exception as e:
        status = {
            "time": now_iso(),
            "error": str(e),
            "to": TO_NUMBER,
            "from": FROM_NUMBER,
        }
        print(f"[{now_iso()}] SMS attempt failed: {status}")

    # Append to log
    entries = load_log()
    entries.append(status)
    save_log(entries)

if __name__ == "__main__":
    main()
