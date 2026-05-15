#!/usr/bin/env python3
"""
Voice Reminder Heartbeat
Runs every 10 minutes to send any due or overdue reminders via Twilio SMS.
Loads Twilio credentials from .env file so it works in Bash and scheduler loops.
"""

import os
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

# === LOAD .ENV FILE (correct project path) ===
load_dotenv("/home/rafa1215/consensus-project/.env")

# === PATHS ===
REMINDER_LOG = "/home/rafa1215/memory/logs/reminders/voice_reminders.log"
HEARTBEAT_LOG = "/home/rafa1215/memory/logs/heartbeat/voice_reminder_heartbeat.log"

# === TWILIO CONFIG ===
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.environ.get("TWILIO_FROM_NUMBER")
TWILIO_TO = os.environ.get("TWILIO_TO_NUMBER")

def log_message(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(HEARTBEAT_LOG), exist_ok=True)
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def send_sms(message):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        msg = client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        log_message(f"SMS sent: SID {msg.sid}")
    except Exception as e:
        log_message(f"ERROR sending SMS: {e}")

def ensure_log_exists():
    if not os.path.exists(REMINDER_LOG):
        os.makedirs(os.path.dirname(REMINDER_LOG), exist_ok=True)
        with open(REMINDER_LOG, "w") as f:
            f.write("")
        log_message(f"Created missing reminder log at {REMINDER_LOG}")

def check_reminders():
    ensure_log_exists()

    now = datetime.now()
    pending = []

    with open(REMINDER_LOG, "r") as f:
        for line in f:
            try:
                ts_str, reminder_text = line.strip().split("|", 1)
                reminder_time = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
                if reminder_time <= now:  # due or overdue
                    pending.append((reminder_time, reminder_text))
            except Exception:
                continue

    if not pending:
        log_message("No due reminders found.")
        return

    for reminder_time, reminder_text in pending:
        send_sms(f"Reminder: {reminder_text}")

    # Keep only future reminders
    remaining = []
    with open(REMINDER_LOG, "r") as f:
        for line in f:
            try:
                ts_str, reminder_text = line.strip().split("|", 1)
                reminder_time = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
                if reminder_time > now:
                    remaining.append(line)
            except Exception:
                continue
    with open(REMINDER_LOG, "w") as f:
        f.writelines(remaining)

if __name__ == "__main__":
    log_message("Running voice reminder heartbeat check...")
    check_reminders()
