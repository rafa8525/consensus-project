from common.twilio_guard import send_sms
import os
import json
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
env_path = "/home/rafa1215/consensus-project/memory/.env"
load_dotenv(dotenv_path=env_path)

# Fallback: inject variables manually if missing
if not all([os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"),
            os.getenv("TWILIO_FROM_NUMBER"), os.getenv("TWILIO_TO_NUMBER")]):
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ.setdefault(key, value)

# Load Twilio credentials
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

# Setup daily SMS log path
log_dir = "/home/rafa1215/consensus-project/memory/logs/sms"
os.makedirs(log_dir, exist_ok=True)
log_date = datetime.now().strftime("%Y-%m-%d")
log_file_path = os.path.join(log_dir, f"{log_date}_sms_log.md")

# Setup fallback error log
error_log_path = os.path.join(log_dir, "sms_errors.md")

# Send SMS and log
for reminder in reminders.get("reminders", []):
    try:
        message = send_sms(
            body=reminder["message"],
            from_=from_number,
            to=to_number
        )
        print(f"[✔] SMS sent: SID {message.sid}")
        log_entry = f"{datetime.now()} | SMS sent: {reminder['message'][:50]}... SID: {message.sid}\n"
        with open(log_file_path, "a") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"[ERROR] Failed to send SMS: {e}")
        failure_log = f"{datetime.now()} | SMS FAILED: {reminder['message'][:50]}...\n"
        with open(error_log_path, "a") as err_log:
            err_log.write(failure_log)
