#!/usr/bin/env python3
import json
import time
import datetime
import os
from pathlib import Path
from twilio.rest import Client

# ==== CONFIG ====
BASE_DIR = Path("/home/rafa1215/consensus-project/memory")
REMINDER_FILE = BASE_DIR / "config" / "reminders.json"
LOG_FILE = BASE_DIR / "logs" / "sms_sent_today.log"

# Twilio credentials (ensure these are set in PythonAnywhere environment variables)
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_PHONE")
TWILIO_TO = os.getenv("TWILIO_TO")

client = Client(TWILIO_SID, TWILIO_AUTH)

# ==== FUNCTIONS ====
def load_reminders():
    with open(REMINDER_FILE) as f:
        data = json.load(f)
    return data.get("reminders", [])

def load_sent_today():
    if not LOG_FILE.exists():
        return set()
    today = datetime.date.today().isoformat()
    sent = set()
    with open(LOG_FILE) as f:
        for line in f:
            if line.startswith(today):
                sent.add(line.strip().split("|")[1])  # message text
    return sent

def log_sent(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.date.today().isoformat()}|{message}\n")

def send_sms(message):
    print(f"[SEND] {message}")
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        log_sent(message)
    except Exception as e:
        print(f"[ERROR sending SMS] {e}")

def matches_now(reminder):
    now = datetime.datetime.now()
    reminder_time = reminder.get("time")
    day = reminder.get("day", None)
    interval_days = reminder.get("interval_days", None)

    # Match day-of-week
    if day and now.strftime("%A") != day:
        return False

    # Match exact time
    if reminder_time and now.strftime("%H:%M") != reminder_time:
        return False

    # Handle interval_days (like every 14 days)
    if interval_days:
        days_since_epoch = (now.date() - datetime.date(1970, 1, 1)).days
        if days_since_epoch % interval_days != 0:
            return False

    return True

# ==== MAIN LOOP ====
print("[START] Fixed Reminder Scheduler running...")
while True:
    try:
        reminders = load_reminders()
        sent_today = load_sent_today()
        now = datetime.datetime.now().strftime("%H:%M")

        for reminder in reminders:
            if matches_now(reminder):
                message = reminder["message"]
                if message not in sent_today:
                    send_sms(message)

        # Sleep 60 sec and check again
        time.sleep(60)

    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(60)
