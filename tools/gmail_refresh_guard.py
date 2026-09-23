#!/usr/bin/env python3
"""
Canonical Gmail OAuth refresh/health guard.

Uses the same OAuth token as the active Gmail agents:
    /home/rafa1215/.secrets/google/token_gmail.json

This guard never starts an interactive OAuth flow. If the token is missing,
gmail_auth_setup.py must be run manually once.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


TOKEN = Path("/home/rafa1215/.secrets/google/token_gmail.json")
LOG = Path(
    "/home/rafa1215/consensus-project/"
    "memory/logs/system/gmail_refresh_guard.log"
)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{stamp()} {message}\n")


def main() -> int:
    log("start gmail_refresh_guard")

    if not TOKEN.exists():
        log(f"error missing_oauth_token path={TOKEN}")
        return 2

    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN.write_text(creds.to_json(), encoding="utf-8")
            TOKEN.chmod(0o600)
            log("oauth token refreshed")

        if not creds.valid:
            log("error oauth_credentials_invalid")
            return 1

        service = build(
            "gmail",
            "v1",
            credentials=creds,
            cache_discovery=False,
        )

        profile = service.users().getProfile(userId="me").execute()
        address = profile.get("emailAddress", "unknown")

        log(f"ok gmail_api_authenticated account={address}")
        return 0

    except Exception as exc:
        log(f"error {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
