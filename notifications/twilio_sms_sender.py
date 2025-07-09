from twilio.rest import Client
import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv(dotenv_path=".env")

# ✅ Read Twilio credentials and phone numbers
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_PHONE = os.getenv("TWILIO_FROM_NUMBER")   # Your Twilio number (e.g., +18886607830)
TO_PHONE = os.getenv("TWILIO_TO_NUMBER")       # Your target number (e.g., +16502283267)

def send_sms(message: str):
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=FROM_PHONE,  # ✅ Correct Twilio number usage
            to=TO_PHONE
        )
        print(f"✅ SMS sent. SID: {message.sid}")
    except Exception as e:
        print(f"❌ SMS failed: {str(e)}")

# ✅ Test run (manual or --test trigger)
if __name__ == "__main__":
    send_sms("✅ Twilio Test Successful. Rafael, this is confirmation your SMS system is now live.")
