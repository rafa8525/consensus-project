# send_reminder_util.py

from twilio.rest import Client
import os

def send_reminder(message="Reminder: Don't forget to check in!"):
    try:
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_number = os.environ.get("TWILIO_FROM_NUMBER")
        to_number = os.environ.get("TWILIO_TO_NUMBER")

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )

        return message.sid
    except Exception as e:
        return None
