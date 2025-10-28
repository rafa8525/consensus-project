#!/usr/bin/env python3
"""
voice_gmail_auth.py
Version: 4.0 (Final Fix for PythonAnywhere)
Purpose:
  Authenticate with Gmail API in a console-only environment (PythonAnywhere).
  Uses manual copy-paste OAuth flow and saves token.json for reuse.
"""

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # ✅ Allow http://localhost in console flows

import json
import traceback
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# === PATHS ===
BASE = Path("/home/rafa1215/consensus-project")
CREDENTIALS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"

# === SCOPES ===
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# === SAVE CREDS ===
def save_credentials(creds):
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    with open(TOKEN_FILE, 'w') as token_file:
        json.dump(token_data, token_file)
    print("✅ Credentials saved to token.json")

# === LOAD CREDS ===
def load_credentials():
    if not TOKEN_FILE.exists():
        return None
    with open(TOKEN_FILE, 'r') as token_file:
        data = json.load(token_file)
    return Credentials(
        token=data['token'],
        refresh_token=data.get('refresh_token'),
        token_uri=data['token_uri'],
        client_id=data['client_id'],
        client_secret=data['client_secret'],
        scopes=data['scopes']
    )

# === AUTHENTICATE ===
def authenticate_gmail():
    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        scopes=SCOPES
    )
    flow.redirect_uri = 'http://localhost'  # ✅ works with insecure transport enabled

    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )

    print("\n🔐 Visit this URL in your browser and log in:")
    print(auth_url)
    print("\n⚠️ After login, you will be redirected to http://localhost/... (will show an error).")
    print("Copy the FULL URL from your browser and paste it below.\n")

    authorization_response = input("✏️ Paste the full redirect URL here: ").strip()
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials
    save_credentials(creds)
    return creds

# === SERVICE BUILDER ===
def get_gmail_service():
    creds = load_credentials()

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("♻️ Refreshing token...")
            creds.refresh(Request())
            save_credentials(creds)
        else:
            creds = authenticate_gmail()

    return build("gmail", "v1", credentials=creds)

# === MAIN TEST ===
if __name__ == "__main__":
    try:
        service = get_gmail_service()
        profile = service.users().getProfile(userId='me').execute()
        print(f"\n📨 Authenticated as: {profile['emailAddress']}")
        print(f"✉️ Total messages: {profile.get('messagesTotal', 'N/A')}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        traceback.print_exc()
