
from twilio.rest import Client
import os

# Load environment variables (update these if hardcoding)
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC4b4d18bdc5bc1b13f7bf2220a9d02287")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "3cd125fe97e04a2203ea7e24c6e9f4d8")
MESSAGING_SERVICE_SID = os.getenv("TWILIO_MSG_SERVICE_SID", "MG6f8cbdafe7ab9d0de20050d8c0a69055")
TARGET_PHONE = os.getenv("TARGET_PHONE_NUMBER", "+16502283267")  # Replace with Rafael's number

def send_sms(message: str):
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            messaging_service_sid=MESSAGING_SERVICE_SID,
            to=TARGET_PHONE
        )
        print(f"✅ SMS sent. SID: {message.sid}")
    except Exception as e:
        print(f"❌ SMS failed: {str(e)}")

# Example usage:
if __name__ == "__main__":
    send_sms("Test message from AI Consensus System.")
