#!/usr/bin/env python3
"""
gmail_refresh_guard_v3.py
Uses Google service-account credentials (no browser auth required).
"""

import datetime, traceback
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2 import service_account

BASE = Path("/home/rafa1215/consensus-project")
KEY = BASE / "memory/system/service_account.json"
LOG = BASE / "memory/logs/email/connection_guard.md"
SCOPES = ["https://mail.google.com/"]

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n")

def main():
    log("---- Gmail Refresh Guard v3 Started ----")
    try:
        creds = service_account.Credentials.from_service_account_file(str(KEY), scopes=SCOPES)
        build("gmail", "v1", credentials=creds)   # simple connectivity test
        log("✅ Gmail service-account authentication succeeded.\n")
    except Exception as e:
        log(f"❌ Gmail Guard v3 failed – {type(e).__name__}: {e}")
        log(traceback.format_exc())

if __name__ == "__main__":
    main()
