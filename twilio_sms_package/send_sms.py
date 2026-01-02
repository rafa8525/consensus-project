#!/usr/bin/env python3
from common import twilio_guard
import os
from pathlib import Path
from dotenv import load_dotenv
from twilio.rest import Client

def main() -> int:
    # Always load the canonical env file (the one you actually maintain)
    env_path = Path.home() / "reminder-api" / ".env"
    load_dotenv(dotenv_path=env_path)

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token  = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    to_number   = os.getenv("TWILIO_TO_NUMBER")

    missing = [k for k,v in [
        ("TWILIO_ACCOUNT_SID", account_sid),
        ("TWILIO_AUTH_TOKEN", auth_token),
        ("TWILIO_FROM_NUMBER", from_number),
        ("TWILIO_TO_NUMBER", to_number),
    ] if not v]
    if missing:
        print("ERROR: Missing env vars:", ", ".join(missing))
        print("Loaded from:", str(env_path))
        return 2

    client = Client(account_sid, auth_token)
    msg = twilio_guard.send_sms(client, 
        body="Hi Rafael, are you going on your 10:30 AM walk today?",
        from_=from_number,
        to=to_number,
    )
    print("OK: SMS sent. SID:", msg.sid)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())