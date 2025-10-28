#!/usr/bin/env python3
"""
calendar_event_creator.py
Purpose:
  Create Google Calendar events on the shared "Rafael Lopez" calendar
  using the permanent service-account key.
"""

import datetime
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2 import service_account

# === Paths ===
BASE = Path("/home/rafa1215/consensus-project")
KEY_FILE = BASE / "memory/system/service_account.json"
LOG_FILE = BASE / "memory/logs/calendar/event_creator.log"

# === Scopes ===
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# === Logging helper ===
def log(msg):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

# === Event creation ===
def create_event(summary, start_time, end_time=None, timezone="America/Los_Angeles", description=None):
    """
    summary: short event title
    start_time / end_time: datetime objects (UTC or local)
    timezone: e.g. "America/Los_Angeles"
    description: optional details
    """
    log(f"Creating event: {summary} at {start_time}")

    creds = service_account.Credentials.from_service_account_file(str(KEY_FILE), scopes=SCOPES)
    service = build("calendar", "v3", credentials=creds)

    # default end time = start + 30 min
    if end_time is None:
        end_time = start_time + datetime.timedelta(minutes=30)

    event = {
        "summary": summary,
        "description": description or "",
        "start": {"dateTime": start_time.isoformat(), "timeZone": timezone},
        "end": {"dateTime": end_time.isoformat(), "timeZone": timezone},
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    log(f"✅ Event created: {created.get('htmlLink')}")
    return created

# === Example direct run ===
if __name__ == "__main__":
    now = datetime.datetime.now()
    start = now + datetime.timedelta(minutes=10)
    end = start + datetime.timedelta(minutes=30)
    create_event("Test Event from Service Account", start, end, description="Automated test")
    log("---- Script completed ----\n")
