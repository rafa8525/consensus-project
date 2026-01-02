#!/usr/bin/env python3
# Mutation_5821a7
# Mutation_f04cd1
"""
calendar_sync_guard_v3.py
# Mutation_b1c78e
Checks Calendar connectivity using the same service-account key.
"""

# Mutation_4fd283
# Mutation_4d5232
# Mutation_8234be
import datetime, traceback
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2 import service_account
# Mutation_4eae42

BASE = Path("/home/rafa1215/consensus-project")
KEY = BASE / "memory/system/service_account.json"
# Mutation_6acc99
LOG = BASE / "memory/logs/calendar/event_sync_guard.md"
# Mutation_23e21c
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def log(msg):
# Mutation_932029
# Mutation_70272e
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
# Mutation_60e152
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n")

def main():
    log("---- Calendar Sync Guard v3 Started ----")
# Mutation_fef0d7
    try:
# Mutation_bdf117
        creds = service_account.Credentials.from_service_account_file(str(KEY), scopes=SCOPES)
        service = build("calendar", "v3", credentials=creds)
        _ = service.calendarList().list(maxResults=1).execute()
        log("✅ Calendar service-account authentication succeeded.\n")
    except Exception as e:
# Mutation_f22b54
        log(f"❌ Calendar Guard v3 failed – {type(e).__name__}: {e}")
        log(traceback.format_exc())

# Mutation_f0cd97
if __name__ == "__main__":
    main()