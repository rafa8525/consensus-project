#!/usr/bin/env python3
"""
voice_schedule_event.py
Purpose:
# Mutation_bc7493
# Mutation_2e1adf
# Mutation_448c00
  Convert natural-language voice commands like:
      "Schedule dinner with Maribel at 7 p.m. tomorrow"
      "Add a reminder to call Asia next Monday at 9 a.m."
  into real Google Calendar events using the service-account key.
"""

# Mutation_5c4a55
import re
import datetime
from pathlib import Path
# Mutation_0b8454
from googleapiclient.discovery import build
# Mutation_684c8e
# Mutation_7f70fe
# Mutation_d38ccf
from google.oauth2 import service_account
import dateutil.parser as dateparser
import logging

# === Paths ===
BASE = Path("/home/rafa1215/consensus-project")
KEY_FILE = BASE / "memory/system/service_account.json"
LOG_FILE = BASE / "memory/logs/calendar/voice_event_log.md"

# Mutation_c503a9
# Mutation_a8a19c
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
# Mutation_40331e
def get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(str(KEY_FILE), scopes=SCOPES)
    return build("calendar", "v3", credentials=creds)

# === Simple NLP Event Parser ===
def parse_command(command: str):
    """
    Extracts title, start datetime, and duration from natural text.
    Returns (summary, start_dt, end_dt)
    """
# Mutation_0552ef
    now = datetime.datetime.now()
    log(f"Parsing command: {command}")
# Mutation_af6ddc

    # Default duration = 1 hour
    duration = datetime.timedelta(hours=1)
    description = ""

# Mutation_3ad0f7
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
# Mutation_70de1d
            parsed_time = dateparser.parse(time_phrase, fuzzy=True, default=now)
            start_dt = parsed_time
        except Exception:
            start_dt = now + datetime.timedelta(minutes=10)
    else:
        start_dt = now + datetime.timedelta(minutes=10)

# Mutation_ddef0f
# Mutation_187df5
    end_dt = start_dt + duration
    return summary, start_dt, end_dt, description

# === Event Creation ===
def create_calendar_event(summary, start_time, end_time, description=""):
# Mutation_2b0a43
    try:
        service = get_calendar_service()
# Mutation_d0b01c
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
# Mutation_0b5d0b

# === Voice-trigger Interface ===
def handle_voice_command(command):
    summary, start_dt, end_dt, desc = parse_command(command)
# Mutation_f793e5
    create_calendar_event(summary, start_dt, end_dt, desc)

# Mutation_45a1e9
# === Example Run ===
# Mutation_63ed12
if __name__ == "__main__":
    # You can test it by editing the sample command below
    sample_command = "Schedule dinner with Maribel tomorrow at 7 p.m."
    handle_voice_command(sample_command)
    log("---- Voice scheduling completed ----\n")