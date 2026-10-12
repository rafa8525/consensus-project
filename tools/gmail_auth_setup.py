#!/usr/bin/env python3
"""Headless Gmail OAuth reauthorization for the AI Consensus PythonAnywhere host.

This command requires explicit user approval in a browser. It verifies the
Gmail profile request before replacing the existing token. No credentials,
authorization codes or token values are printed after authorization.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]
SECRETS = Path.home() / ".secrets" / "google"
CREDENTIALS_FILE = SECRETS / "credentials.json"
TOKEN_FILE = SECRETS / "token_gmail.json"


def persist_token_safely(path: Path, credentials) -> None:
    """Atomic, owner-readable-only token update after successful API verification."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(dir=str(path.parent), prefix=".gmail-oauth-", suffix=".tmp")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd = -1
            handle.write(credentials.to_json())
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def verify_gmail_credentials(credentials) -> bool:
    """Exercise a real authorized Gmail API request; building a client is insufficient."""
    from googleapiclient.discovery import build

    service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    profile = service.users().getProfile(userId="me").execute()
    return isinstance(profile, dict) and bool(profile.get("emailAddress"))


def authenticate_gmail() -> bool:
    """Interactive headless OAuth; existing token is preserved on any failure."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not CREDENTIALS_FILE.is_file():
        print("ERROR: Missing OAuth client configuration in private ~/.secrets/google directory.")
        return False

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    flow.redirect_uri = "http://localhost"
    auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")
    print("Open this Google authorization URL in your browser and grant access:")
    print(auth_url)
    print("If localhost shows a connection error, copy the full address bar URL.")
    response = input("Paste the redirected localhost URL in the private PythonAnywhere console: ").strip()
    if not response.startswith("http://localhost"):
        print("ERROR: Expected a localhost OAuth redirect URL. No token was changed.")
        return False

    try:
        flow.fetch_token(authorization_response=response)
        credentials = flow.credentials
        if not getattr(credentials, "refresh_token", None):
            print("ERROR: No refresh token returned. Existing token preserved.")
            return False
        if not verify_gmail_credentials(credentials):
            print("ERROR: Gmail API verification unsuccessful. Existing token preserved.")
            return False
        persist_token_safely(TOKEN_FILE, credentials)
    except Exception as exc:
        # Exception messages may contain OAuth codes, redirect URLs or secrets.
        print(f"ERROR: Authorization or verification failed ({type(exc).__name__}). Existing token preserved.")
        return False

    print("SUCCESS: Gmail API verified; token stored privately with restricted permissions.")
    return True


def load_gmail_credentials():
    from google.oauth2.credentials import Credentials

    if not TOKEN_FILE.is_file():
        raise FileNotFoundError("Gmail OAuth token missing. Run gmail_auth_setup.py.")
    return Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)


def main() -> int:
    return 0 if authenticate_gmail() else 1


if __name__ == "__main__":
    raise SystemExit(main())
