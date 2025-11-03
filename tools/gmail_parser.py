import os
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# ----- CONFIG -----
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
PROJECT_ROOT = os.path.expanduser('~/consensus-project')
CREDENTIALS_PATH = os.path.join(PROJECT_ROOT, 'tools', 'credentials.json')
TOKEN_PATH = os.path.join(PROJECT_ROOT, 'tools', 'token.json')
LOG_PATH = os.path.join(PROJECT_ROOT, 'memory', 'logs', 'system', 'gmail_subjects.log')


def authenticate():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)  # Picks any free port
            with open(TOKEN_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
    return creds


def fetch_subjects(service, max_messages=10):
    results = service.users().messages().list(userId='me', maxResults=max_messages).execute()
    messages = results.get('messages', [])

    subjects = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject']
        ).execute()

        headers = msg_data['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        subjects.append(subject)
    return subjects


def main():
    print("📧 Authenticating with Gmail...")
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    print("📥 Fetching email subjects...")
    subjects = fetch_subjects(service)

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(LOG_PATH, 'a') as log_file:
        log_file.write(f"\n[{timestamp}] Gmail Subject Digest:\n")
        for subject in subjects:
            log_file.write(f"• {subject}\n")

    print(f"✅ {len(subjects)} subject(s) saved to {LOG_PATH}")


if __name__ == '__main__':
    main()
