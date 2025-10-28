import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE = Path("/home/rafa1215/consensus-project")
TOKEN_FILE = BASE / "token.json"

# ✅ Same dual-scope config
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly"
]

def load_credentials():
    if not TOKEN_FILE.exists():
        return None
    with open(TOKEN_FILE, 'r') as f:
        data = json.load(f)
    return Credentials(
        token=data['token'],
        refresh_token=data.get('refresh_token'),
        token_uri=data['token_uri'],
        client_id=data['client_id'],
        client_secret=data['client_secret'],
        scopes=SCOPES
    )

def get_calendar_service():
    creds = load_credentials()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError("Calendar credentials missing or invalid.")
    return build("calendar", "v3", credentials=creds)
