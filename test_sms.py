#!/usr/bin/env python3
# test_sms.py
# Purpose: Verify Twilio credentials + SMS delivery with dotenv support.

import os
import datetime
from dotenv import load_dotenv
from twilio_guard import send_sms

# ====== LOAD ENV ======
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

TO_NUMBER = os.getenv("TEST_SMS_TO", "+16502283267")  # fallback: your number

def main():
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    result = send_sms(to=TO_NUMBER, body=f"Test SMS at {ts}")
    print(f"{ts} -> Result: {result}")

if __name__ == "__main__":
    main()
