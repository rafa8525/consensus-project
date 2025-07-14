# twilio_config_loader.py
import os
from dotenv import load_dotenv

def load_twilio_credentials():
    # Load from .env if available
    load_dotenv(dotenv_path="/home/rafa1215/.env")

    required = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"]
    missing = []

    for key in required:
        if not os.getenv(key):
            missing.append(key)

    if missing:
        print(f"⚠️ Missing Twilio credentials: {', '.join(missing)}")
        return False
    return True
