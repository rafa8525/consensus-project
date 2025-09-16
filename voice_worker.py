#!/usr/bin/env python3
"""
voice_worker.py
Processes queued voice trigger jobs and sends SMS via Twilio.
"""

import os, time, json
from pathlib import Path
from twilio.rest import Client

# Folders
QUEUE_DIR = Path("queue/processing")
DONE_DIR = Path("queue/done")
LOG_FILE = Path("memory/logs/reminders/voice_trigger.md")

QUEUE_DIR.mkdir(parents=True, exist_ok=True)
DONE_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Twilio credentials from environment variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_FROM_NUMBER")
to_number = os.getenv("TWILIO_TO_NUMBER")

client = Client(account_sid, auth_token)

def log(msg: str):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

while True:
    for job_file in QUEUE_DIR.glob("voice_trigger_*.json"):
        job = json.loads(job_file.read_text())
        try:
            client.messages.create(
                body=job["message"],
                from_=from_number,
                to=to_number
            )
            log(f"✅ SMS sent for {job_file.name}")
        except Exception as e:
            log(f"❌ SMS failed for {job_file.name}: {e}")
        job_file.rename(DONE_DIR / job_file.name)
    time.sleep(10)
