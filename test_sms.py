#!/usr/bin/env python3
from common import twilio_guard
# test_sms.py
# Purpose: Minimal SMS send test using Twilio credentials from .env
# Platform: PythonAnywhere-safe. No emojis.

import os
import sys
import datetime
import logging
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.expanduser("~/consensus-project/.env"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def send_test_sms():
    # Pull Twilio vars from environment
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    to_number = os.getenv("TWILIO_TO_NUMBER")

    # Validate
    if not all([account_sid, auth_token, from_number, to_number]):
        logging.error("Missing Twilio credentials in .env")
        return {"status": "error", "reason": "missing_credentials"}

    try:
        client = Client(account_sid, auth_token)
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        body = f"[{ts}] Test SMS from consensus-project"

        msg = clienttwilio_guard.send_sms(client, 
            body=body,
            from_=from_number,
            to=to_number
        )

        logging.info(f"SUCCESS: SMS sent to {to_number}. SID={msg.sid}")
        return {"status": "success", "sid": msg.sid}

    except Exception as e:
        logging.error(f"SMS send failed: {e}")
        return {"status": "error", "reason": str(e)}

if __name__ == "__main__":
    result = send_test_sms()
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"{ts} -> Result: {result}")