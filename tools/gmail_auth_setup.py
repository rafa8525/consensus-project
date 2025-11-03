#!/usr/bin/env python3
"""
gmail_auth_setup.py
Headless Gmail OAuth setup for PythonAnywhere (manual copy-paste flow).

- Works in environments without a local web browser.
- Accepts Gmail + Drive scopes to prevent "scope changed" warnings.
- Saves token for reuse in ~/consensus-project/memory/core/secrets/token_gmail.json
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# -------------------------------------------------------------------
# Allow HTTP redirect (PythonAnywhere is headless)
# -------------------------------------------------------------------
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file"
]

CREDENTIALS_FILE = os.path.expanduser(
    "/home/rafa1215/.secrets/google/credentials.json"
)
TOKEN_FILE = os.path.expanduser(
    "~/consensus-project/memory/core/secrets/token_gmail.json"
)


def authenticate_gmail():
    """
    Manual Gmail OAuth flow.
    Steps:
      1. Copy the printed URL into a browser on your PC/phone.
      2. Approve permissions.
      3. Copy the resulting URL (starts with http://localhost/?code=...)
      4. Paste it here.
    """

    print("\n=== Gmail OAuth Authentication (Headless Mode) ===")

    # 1. Initialize flow
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    flow.redirect_uri = "http://localhost"

    # 2. Generate the authorization URL
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    # 3. Show user instructions
    print("\n" + "=" * 70)
    print("GMAIL AUTHORIZATION INSTRUCTIONS")
    print("=" * 70)
    print("\n1. Open this link in ANY browser (desktop or phone):\n")
    print(auth_url)
    print("\n2. Sign in and click 'Allow' to grant permissions.")
    print("\n3. You'll see a 'localhost refused to connect' error — this is NORMAL.")
    print("4. Copy the full URL from your browser's address bar (starts with http://localhost)")
    print("5. Paste that URL here below.\n")
    print("=" * 70 + "\n")

    # 4. Read the full redirect URL
    authorization_response = input("Paste the full redirect URL here: ").strip()

    # 5. Exchange the code for a token
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as e:
        print(f"\n❌ Error exchanging code for token:\n{e}")
        print("→ Ensure you pasted the *entire* URL starting with http://localhost")
        raise

    creds = flow.credentials

    # 6. Save credentials
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
        "expiry": creds.expiry.isoformat() if creds.expiry else None
    }

    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)

    print(f"\n✅ Credentials saved to: {TOKEN_FILE}")
    print("✅ Gmail authentication completed successfully!\n")

    return creds


def load_gmail_credentials():
    """Load previously saved credentials."""
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError("Token file missing. Run gmail_auth_setup.py first.")
    return Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)


if __name__ == "__main__":
    creds = authenticate_gmail()

    # Verify API access
    try:
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        print(f"\n📧 Authenticated as: {profile.get('emailAddress')}")
        print(f"📨 Total messages: {profile.get('messagesTotal')}\n")
    except Exception as e:
        print(f"\n⚠️ Verification warning: {e}")
        print("If credentials were saved above, Gmail access is still active.\n")
