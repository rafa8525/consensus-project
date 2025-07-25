import os
import json
from twilio.rest import Client
from dotenv import load_dotenv

# Load from .env manually if missing
env_path = "/home/rafa1215/consensus-project/memory/.env"
load_dotenv(dotenv_path=env_path)

# Fallback: Read .env file and inject if needed
if not all([os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"),
            os.getenv("TWILIO_FROM_NUMBER"), os.getenv("TWILIO_TO_NUMBER")]):
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ.setdefault(key, value)

# Read variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_FROM_NUMBER")
to_number = os.getenv("TWILIO_TO_NUMBER")

if not all([account_sid, auth_token, from_number, to_number]):
    print("[ERROR] Missing Twilio environment variables.")
    exit(1)

# Load reminders
reminder_path = "/home/rafa1215/consensus-project/memory/config/reminders.json"
if not os.path.exists(reminder_path):
    print("[ERROR] Reminder config not found.")
    exit(1)

with open(reminder_path, "r") as file:
    reminders = json.load(file)

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Send voice reminders
for reminder in reminders.get("reminders", []):
    try:
        message = client.calls.create(
            twiml=f'<Response><Say>{reminder["message"]}</Say></Response>',
            to=to_number,
            from_=from_number
        )
        print(f"[✔] Call initiated: SID {message.sid}")
    except Exception as e:
        print(f"[ERROR] Failed to send call: {e}")
