# validate_twilio_credentials.py

import os
from twilio.rest import Client

def validate_twilio():
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    to_number = os.getenv("TWILIO_TO_NUMBER")

    if not all([sid, token, from_number, to_number]):
        print("❌ Missing one or more required Twilio environment variables.")
        return False

    try:
        client = Client(sid, token)
        # Test API call
        accounts = client.api.accounts.list(limit=1)
        print("✅ Twilio credentials are valid.")
        return True
    except Exception as e:
        print(f"❌ Twilio validation failed: {e}")
        return False

if __name__ == "__main__":
    validate_twilio()
