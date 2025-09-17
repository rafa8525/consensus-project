#!/usr/bin/env python3
# twilio_guard.py
# Purpose: Safe Twilio SMS sender with dotenv loading, sandbox guardrails, and logging.

import os
import sys
import json
import datetime
import logging
from pathlib import Path
from dotenv import load_dotenv
from twilio.rest import Client

# ====== CONFIG ======
PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIR = PROJECT_ROOT / "memory" / "logs" / "system"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "twilio_guard.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ====== LOAD ENV ======
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
SAFE_MODE = os.getenv("SMS_SAFE_MODE", "ON").upper()  # ON = sandbox; OFF = live

def check_credentials():
    return all([ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER])

# ====== SMS FUNCTION ======
def send_sms(to: str, body: str):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    if not check_credentials():
        msg = f"[{ts}] ERROR: Missing Twilio credentials in .env"
        print(msg)
        logging.error(msg)
        return {"status": "error", "reason": "missing_credentials"}

    if SAFE_MODE == "ON":
        msg = f"[{ts}] SMS (sandbox, not sent): to={to}, body={body}"
        print(msg)
        logging.info(msg)
        return {"status": "sandbox", "to": to, "body": body}

    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        sms = client.messages.create(
            body=body,
            from_=FROM_NUMBER,
            to=to
        )
        result = {"status": "sent", "sid": sms.sid}
        msg = f"[{ts}] SUCCESS: SMS sent to {to}, SID={sms.sid}"
        print(msg)
        logging.info(msg)
        return result
    except Exception as e:
        err = f"[{ts}] ERROR sending SMS: {repr(e)}"
        print(err)
        logging.error(err)
        return {"status": "error", "reason": str(e)}

if __name__ == "__main__":
    print("twilio_guard.py loaded. Use send_sms(to, body) in scripts.")
