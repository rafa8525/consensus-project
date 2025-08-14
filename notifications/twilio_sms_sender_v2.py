from common.twilio_guard import send_sms

from twilio.rest import Client
import os
import json
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Load credentials from environment
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
MESSAGING_SERVICE_SID = os.getenv("TWILIO_MSG_SERVICE_SID")

# Load contacts
with open("contacts.json") as f:
    CONTACTS = json.load(f)

def send_sms_to(name: str, message: str):
    name = name.strip().lower()
    if name not in CONTACTS:
        print(f"❌ No phone number found for '{name}'")
        return
    to_number = CONTACTS[name]
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        sms = send_sms(
            body=message,
            messaging_service_sid=MESSAGING_SERVICE_SID,
            to=to_number
        )
        print(f"✅ SMS sent to {name} ({to_number}). SID: {sms.sid}")
    except Exception as e:
        print(f"❌ Failed to send SMS: {str(e)}")

# Example use
if __name__ == "__main__":
    send_sms_to("maribel", "What do you want me to pick up for dinner?")
