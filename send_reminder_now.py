import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from the notifications folder
load_dotenv(dotenv_path="/home/rafa1215/consensus-project/notifications/.env")

# Twilio credentials and phone numbers
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
user_to_number = os.getenv("RAFAEL_PHONE_NUMBER")

# Reminder message
message_body = "🔔 Reminder: You scheduled this alert earlier — please check the item you emailed about at 1:07 PM."

# Send SMS
def send_sms():
    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            to=user_to_number,
            from_=twilio_from_number,
            body=message_body
        )
        print(f"✅ SMS sent. SID: {message.sid}")
    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")

if __name__ == "__main__":
    send_sms()
