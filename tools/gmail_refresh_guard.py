#!/usr/bin/env python3
"""
gmail_refresh_guard.py
Version: 2.0
Author: AI Consensus System
Purpose:
  - Maintain and repair Gmail API authentication automatically.
  - Self-generate missing tokens via OAuth flow using client_secret.json.
  - Log all status messages and recover from any authentication failure.

Requirements:
  - client_secret.json stored at ~/consensus-project/memory/system/
  - google-auth, google-auth-oauthlib, google-auth-httplib2 installed
"""

import os
import datetime
import traceback
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# === PATHS ===
BASE_DIR = Path("/home/rafa1215/consensus-project")
SYSTEM_DIR = BASE_DIR / "memory/system"
TOKEN_PATH = SYSTEM_DIR / "google_token.json"
CLIENT_SECRET = SYSTEM_DIR / "client_secret.json"
LOG_PATH = BASE_DIR / "memory/logs/email/connection_guard.md"

# === SCOPES ===
SCOPES = ["https://mail.google.com/"]

# === LOGGING ===
def log(message: str):
    """Write timestamped messages to connection_guard.md"""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

# === TOKEN REFRESHER ===
def get_or_refresh_gmail_token():
    """Create or refresh Gmail OAuth token automatically."""
    SYSTEM_DIR.mkdir(parents=True, exist_ok=True)
    creds = None

    # Load existing credentials if available
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        except Exception as e:
            log(f"⚠️ Could not load existing token file: {e}")
            log(traceback.format_exc())

    try:
        # If credentials exist and are valid
        if creds and creds.valid:
            log("🟢 Gmail token is valid; no refresh needed.")
            return True

        # If credentials exist but are expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, "w") as token_file:
                token_file.write(creds.to_json())
            log("✅ Gmail token refreshed successfully.")
            return True

        # If no valid token exists, generate a new one
        if CLIENT_SECRET.exists():
            log("⚠️ No valid Gmail token found. Starting OAuth flow.")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET), SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w") as token_file:
                token_file.write(creds.to_json())
            log("✅ New Gmail token created successfully.")
            return True
        else:
            log("❌ Missing client_secret.json. Cannot authenticate Gmail.")
            return False

    except Exception as e:
        log(f"❌ Gmail token refresh error: {type(e).__name__} - {e}")
        log(traceback.format_exc())
        return False

# === MAIN EXECUTION ===
def main():
    log("---- Gmail Refresh Guard Started ----")
    success = get_or_refresh_gmail_token()
    if success:
        log("✅ Gmail Refresh Guard completed successfully.\n")
    else:
        log("❌ Gmail Refresh Guard failed.\n")

if __name__ == "__main__":
    main()
