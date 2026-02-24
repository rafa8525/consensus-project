#!/usr/bin/env python3
"""
gmail_refresh_guard_v3.py

Purpose:
- Lightweight “can I authenticate to Gmail?” connectivity guard using a Google service account.
- Writes a heartbeat-style log line every run to the system log path monitored by core_monitors_bundle.

Expected inputs:
- Service account JSON key:
    /home/rafa1215/consensus-project/memory/system/service_account.json

Outputs:
- Log file (append-only):
    /home/rafa1215/memory/logs/system/gmail_refresh_guard_v3.log

Notes:
- Requires: google-api-python-client, google-auth
- Scope uses full Gmail access ("https://mail.google.com/"). If you prefer read-only, change SCOPES.
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build


BASE = Path("/home/rafa1215/consensus-project")
KEY = BASE / "memory/system/service_account.json"
LOG = Path("/home/rafa1215/memory/logs/system/gmail_refresh_guard_v3.log")
SCOPES = ["https://mail.google.com/"]


def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append_log(line: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{utc_ts()} {line}\n")


def main() -> int:
    append_log("start gmail_refresh_guard_v3")

    if not KEY.exists():
        append_log(f"error missing_service_account_key path={KEY}")
        return 2

    try:
        creds = service_account.Credentials.from_service_account_file(str(KEY), scopes=SCOPES)

        # Minimal connectivity test: build Gmail API client. This will validate credentials.
        # We do not call users().messages().list() to avoid extra API calls/quotas.
        _svc = build("gmail", "v1", credentials=creds, cache_discovery=False)

        append_log("ok gmail_refresh_guard_v3 auth_succeeded")
        return 0
    except Exception as e:
        append_log(f"error gmail_refresh_guard_v3 {type(e).__name__}: {e}")
        tb = traceback.format_exc().strip().replace("\n", " | ")
        append_log(f"trace gmail_refresh_guard_v3 {tb}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())