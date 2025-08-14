from common.twilio_guard import send_sms
import os
from datetime import datetime, date
from twilio.rest import Client
import traceback

# Use environment variables only
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TO_NUMBER = os.getenv("TWILIO_TO_NUMBER")

LOG_FILE_PATH = "/home/rafa1215/reminder-api/memory/logs/reminders/fallback_log.txt"

def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(f"{timestamp} - {message}\n")

def send_reminder(message=None):
    try:
        if not message:
            message = "Log today’s work notes or progress update."

        write_log("📤 Attempting Twilio SMS send...")
        write_log(f"ENV CHECK — FROM: {TWILIO_FROM_NUMBER}, TO: {TO_NUMBER}")

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        twilio_msg = send_sms(
            to=TO_NUMBER,
            from_=TWILIO_FROM_NUMBER,
            body=message
        )

        write_log("✅ Twilio message SID: " + twilio_msg.sid)
        write_log("Reminder sent: " + message + "\n")

    except Exception as e:
        write_log("❌ Full Exception Trace:\n" + traceback.format_exc())
        write_log("⚠️ Twilio message send failed.\n")

# Git push fallback log
log_date = date.today().isoformat()
txt_log = "/home/rafa1215/reminder-api/memory/logs/reminders/fallback_log.txt"
md_log = f"/home/rafa1215/consensus-project/memory/logs/reminders/fallback_log_{log_date}.md"

os.system(f"cp {txt_log} {md_log}")
os.chdir("/home/rafa1215/consensus-project")
os.system(f"git add -f memory/logs/reminders/fallback_log_{log_date}.md")
os.system(f"git commit -m '🕙 Reminder fallback log for {log_date}'")
os.system("git pull --rebase origin v1.1-dev")
os.system("git push")
