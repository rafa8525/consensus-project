#!/usr/bin/env python3
"""
voice_schedule_event.py
Purpose:
  Convert natural-language voice commands like:
      "Schedule dinner with Maribel at 7 p.m. tomorrow"
      "Add a reminder to call Asia next Monday at 9 a.m."
  into real Google Calendar events using the service-account key.
"""

import re
import datetime
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2 import service_account
import dateutil.parser as dateparser
import logging

# === Paths ===
BASE = Path("/home/rafa1215/consensus-project")
KEY_FILE = BASE / "memory/system/service_account.json"
LOG_FILE = BASE / "memory/logs/calendar/voice_event_log.md"

# === Scopes ===
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# === Logging Setup ===
def log(msg):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

# === Google Service Auth ===
def get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(str(KEY_FILE), scopes=SCOPES)
    return build("calendar", "v3", credentials=creds)

# === Simple NLP Event Parser ===
def parse_command(command: str):
    """
    Extracts title, start datetime, and duration from natural text.
    Returns (summary, start_dt, end_dt)
    """
    now = datetime.datetime.now()
    log(f"Parsing command: {command}")

    # Default duration = 1 hour
    duration = datetime.timedelta(hours=1)
    description = ""

    # Basic keyword extraction
    if command.lower().startswith("schedule"):
        summary = command.replace("schedule", "", 1).strip().capitalize()
    elif command.lower().startswith("add"):
        summary = command.replace("add", "", 1).strip().capitalize()
    else:
        summary = command.strip().capitalize()

    # Try parsing datetime expressions
    match = re.search(r"(at|on)\s(.+)", command, re.IGNORECASE)
    if match:
        time_phrase = match.group(2)
        try:
            parsed_time = dateparser.parse(time_phrase, fuzzy=True, default=now)
            start_dt = parsed_time
        except Exception:
            start_dt = now + datetime.timedelta(minutes=10)
    else:
        start_dt = now + datetime.timedelta(minutes=10)

    end_dt = start_dt + duration
    return summary, start_dt, end_dt, description

# === Event Creation ===
def create_calendar_event(summary, start_time, end_time, description=""):
    try:
        service = get_calendar_service()
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "America/Los_Angeles"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "America/Los_Angeles"},
        }
        created = service.events().insert(calendarId="primary", body=event).execute()
        log(f"✅ Event created: {summary} | {created.get('htmlLink')}")
    except Exception as e:
        log(f"❌ Failed to create event: {e}")

# === Voice-trigger Interface ===
def handle_voice_command(command):
    summary, start_dt, end_dt, desc = parse_command(command)
    create_calendar_event(summary, start_dt, end_dt, desc)

# === Example Run ===
if __name__ == "__main__":
    # You can test it by editing the sample command below
    sample_command = "Schedule dinner with Maribel tomorrow at 7 p.m."
    handle_voice_command(sample_command)
    log("---- Voice scheduling completed ----\n")
