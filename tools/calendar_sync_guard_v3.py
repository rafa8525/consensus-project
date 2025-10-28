#!/usr/bin/env python3
"""
calendar_sync_guard_v3.py
Checks Calendar connectivity using the same service-account key.
"""

import datetime, traceback
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2 import service_account

BASE = Path("/home/rafa1215/consensus-project")
KEY = BASE / "memory/system/service_account.json"
LOG = BASE / "memory/logs/calendar/event_sync_guard.md"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n")

def main():
    log("---- Calendar Sync Guard v3 Started ----")
    try:
        creds = service_account.Credentials.from_service_account_file(str(KEY), scopes=SCOPES)
        service = build("calendar", "v3", credentials=creds)
        _ = service.calendarList().list(maxResults=1).execute()
        log("✅ Calendar service-account authentication succeeded.\n")
    except Exception as e:
        log(f"❌ Calendar Guard v3 failed – {type(e).__name__}: {e}")
        log(traceback.format_exc())

if __name__ == "__main__":
    main()
