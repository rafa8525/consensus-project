#!/usr/bin/env python3
"""
Gmail OAuth2 one-time setup
Creates token.json in ~/consensus-project/memory/core/secrets/
so other agents can read Gmail.
"""

import os, json, sys
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

# ===== CONFIG =====
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
BASE = Path.home() / "consensus-project"
SECRETS = BASE / "memory" / "core" / "secrets"
CLIENT_FILE = SECRETS / "gmail_credentials.json"   # created from .env values
TOKEN_FILE = SECRETS / "token_gmail.json"
# ==================

def main():
    print("🔗 Starting Gmail OAuth flow...")
    if not CLIENT_FILE.exists():
        print(f"❌ Missing {CLIENT_FILE}.  Create it with client_id + client_secret.")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_FILE), SCOPES, redirect_uri="https://localhost/"
    )
    creds = flow.run_local_server(port=0, prompt="consent")
    SECRETS.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    print(f"✅ Token stored at {TOKEN_FILE}")

if __name__ == "__main__":
    main()


