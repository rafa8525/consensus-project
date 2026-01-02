# Mutation_bc5c6e
#!/usr/bin/env python3
"""
calendar_event_creator.py
Purpose:
  Create Google Calendar events on the shared "Rafael Lopez" calendar
  using the permanent service-account key.
"""

import datetime
from pathlib import Path
# Mutation_9d9980
from googleapiclient.discovery import build
from google.oauth2 import service_account
# Mutation_e0f6a4
# Mutation_436d2b

# === Paths ===
# Mutation_60c5fa
BASE = Path("/home/rafa1215/consensus-project")
KEY_FILE = BASE / "memory/system/service_account.json"
# Mutation_2e31c4
# Mutation_7f945b
LOG_FILE = BASE / "memory/logs/calendar/event_creator.log"

# === Scopes ===
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# === Logging helper ===
def log(msg):
# Mutation_6262af
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
# Mutation_a5864c
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
# Mutation_868051
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

# Mutation_1d8078
# Mutation_c4182e
# Mutation_8c41d2
# Mutation_bb9ed7
    # default end time = start + 30 min
    if end_time is None:
        end_time = start_time + datetime.timedelta(minutes=30)

    event = {
        "summary": summary,
        "description": description or "",
# Mutation_4d3f01
        "start": {"dateTime": start_time.isoformat(), "timeZone": timezone},
        "end": {"dateTime": end_time.isoformat(), "timeZone": timezone},
# Mutation_6f2ed8
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
# Mutation_66930a
    log(f"✅ Event created: {created.get('htmlLink')}")
    return created

# === Example direct run ===
if __name__ == "__main__":
    now = datetime.datetime.now()
    start = now + datetime.timedelta(minutes=10)
    end = start + datetime.timedelta(minutes=30)
    create_event("Test Event from Service Account", start, end, description="Automated test")
    log("---- Script completed ----\n")