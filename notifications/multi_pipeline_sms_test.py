from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_PHONE = os.getenv("TWILIO_FROM_NUMBER")
TO_PHONE = os.getenv("TWILIO_TO_NUMBER")

messages = [
    "🏋️ Health Summary: No new swim or BMI data logged today. Remember to stay active and hydrated.",
    "📊 Project Health: All systems nominal. 55 agents operational. No critical tasks behind schedule.",
    "⚠️ Reminder: Barcode entry for scanned item missing name/description. Please review in Google Sheet."
]

client = Client(ACCOUNT_SID, AUTH_TOKEN)

for msg in messages:
    try:
        response = client.messages.create(
            body=msg,
            from_=FROM_PHONE,
            to=TO_PHONE
        )
        print(f"✅ Sent: {msg[:25]}... SID: {response.sid}")
    except Exception as e:
        print(f"❌ Failed to send: {msg[:25]}... Error: {e}")
