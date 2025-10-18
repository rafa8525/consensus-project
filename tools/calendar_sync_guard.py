#!/usr/bin/env python3
"""
calendar_sync_guard.py
Purpose:
  - Ensure scheduled events appear correctly in Google Calendar (and sync to Pixel Watch).
  - Detect missing or unsynced events and reinsert them automatically.
  - Log all actions and outcomes for diagnostic tracking.

Requirements:
  - Google Calendar API credentials stored at ~/consensus-project/memory/system/google_token.json
  - Read/write access to primary calendar.

Logging:
  - ~/consensus-project/memory/logs/calendar/event_sync_guard.md
"""

import os
import datetime
import traceback
from pathlib import Path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# === Paths ===
BASE_DIR = Path("/home/rafa1215/consensus-project")
TOKEN_PATH = BASE_DIR / "memory/system/google_token.json"
LOG_PATH = BASE_DIR / "memory/logs/calendar/event_sync_guard.md"
EVENT_LOG = BASE_DIR / "memory/logs/calendar/event_log.md"

# === Setup ===
def log(message: str):
    """Append log messages with timestamps."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

def load_creds():
    """Load and refresh Google credentials."""
    if not TOKEN_PATH.exists():
        log("❌ Token file missing. Calendar sync cannot continue.")
        return None
    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), ["https://www.googleapis.com/auth/calendar"])
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, "w") as token_file:
                token_file.write(creds.to_json())
            log("🔄 Token refreshed successfully for Calendar API.")
        return creds
    except Exception as e:
        log(f"❌ Error loading credentials: {e}")
        log(traceback.format_exc())
        return None

def check_recent_events(service, window_hours=4):
    """Check for recent events created in the last few hours."""
    now = datetime.datetime.utcnow().isoformat() + "Z"
    time_min = (datetime.datetime.utcnow() - datetime.timedelta(hours=window_hours)).isoformat() + "Z"
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=now,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    log(f"📅 Found {len(events)} recent events in the last {window_hours} hours.")
    return events

def detect_and_repair_missing_event(service):
    """Cross-check event_log.md entries with Google Calendar."""
    if not EVENT_LOG.exists():
        log("⚠️ No event_log.md file found — skipping repair check.")
        return

    with open(EVENT_LOG, "r") as f:
        logged_lines = [line.strip() for line in f.readlines() if "Event:" in line]

    for line in logged_lines[-5:]:  # Check last 5 events
        try:
            parts = line.split("Event:")[1].strip()
            title = parts.split("|")[0].strip()
            if not title:
                continue

            # Search for matching event
            now = datetime.datetime.utcnow().isoformat() + "Z"
            events_result = service.events().list(
                calendarId='primary',
                timeMin=(datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat() + "Z",
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            found = any(title.lower() in e['summary'].lower() for e in events if 'summary' in e)

            if found:
                log(f"✅ Verified event exists: '{title}'")
            else:
                # Attempt reinsertion
                event_body = {
                    'summary': title,
                    'start': {'dateTime': (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).isoformat(), 'timeZone': 'America/Los_Angeles'},
                    'end': {'dateTime': (datetime.datetime.utcnow() + datetime.timedelta(minutes=35)).isoformat(), 'timeZone': 'America/Los_Angeles'},
                }
                service.events().insert(calendarId='primary', body=event_body).execute()
                log(f"♻️ Reinserted missing event: '{title}'")
        except Exception as e:
            log(f"❌ Error checking/reinserting event: {e}")
            log(traceback.format_exc())

def main():
    log("---- Calendar Sync Guard Started ----")
    creds = load_creds()
    if not creds:
        log("❌ No valid credentials. Calendar sync aborted.\n")
        return

    try:
        service = build("calendar", "v3", credentials=creds)
        check_recent_events(service)
        detect_and_repair_missing_event(service)
        log("✅ Calendar sync guard completed successfully.\n")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        log(traceback.format_exc())

if __name__ == "__main__":
    main()
