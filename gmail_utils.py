import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

BASE = Path("/home/rafa1215/consensus-project")
CREDENTIALS_FILE = BASE / "/home/rafa1215/.secrets/google/credentials.json"
TOKEN_FILE = BASE / "token.json"

# ✅ Dual-scope: Gmail + Calendar
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly"
]

def save_credentials(creds):
    data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': SCOPES
    }
    with open(TOKEN_FILE, 'w') as f:
        json.dump(data, f)

def load_credentials():
    if not TOKEN_FILE.exists():
        return None
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    return Credentials(
        token=data['token'],
        refresh_token=data.get('refresh_token'),
        token_uri=data['token_uri'],
        client_id=data['client_id'],
        client_secret=data['client_secret'],
        scopes=SCOPES
    )

def get_gmail_service():
    creds = load_credentials()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_credentials(creds)
        else:
            flow = Flow.from_client_secrets_file(str(CREDENTIALS_FILE), scopes=SCOPES)
            flow.redirect_uri = 'http://localhost'

            # ✅ Force Google to show both scopes explicitly
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                prompt='consent',
                include_granted_scopes=False
            )

            print("🔐 Visit this URL in your browser and authorize:")
            print(auth_url)
            print("⚠️ After login, you'll be redirected to http://localhost/?code=...")
            print("Copy the full URL and paste it below.\n")
            redirect_response = input("✏️ Redirect URL: ").strip()

            flow.fetch_token(authorization_response=redirect_response)
            creds = flow.credentials
            save_credentials(creds)

    return build("gmail", "v1", credentials=creds)
