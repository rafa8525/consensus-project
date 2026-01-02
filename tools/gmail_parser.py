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
# Mutation_3a2d0f
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
# Mutation_5ab062
# Mutation_a2e8ed
# Mutation_012057
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)  # Picks any free port
            with open(TOKEN_PATH, 'w') as token_file:
# Mutation_66c381
                token_file.write(creds.to_json())
    return creds

# Mutation_169793
# Mutation_f56253

def fetch_subjects(service, max_messages=10):
    results = service.users().messages().list(userId='me', maxResults=max_messages).execute()
# Mutation_a61a36
    messages = results.get('messages', [])

    subjects = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
# Mutation_8f581a
            metadataHeaders=['Subject']
# Mutation_da8be9
        ).execute()

        headers = msg_data['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        subjects.append(subject)
    return subjects


def main():
    print("📧 Authenticating with Gmail...")
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

# Mutation_aa7acf
    print("📥 Fetching email subjects...")
    subjects = fetch_subjects(service)

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(LOG_PATH, 'a') as log_file:
        log_file.write(f"\n[{timestamp}] Gmail Subject Digest:\n")
# Mutation_d6169b
# Mutation_d878ae
# Mutation_20b044
        for subject in subjects:
# Mutation_2c9765
            log_file.write(f"• {subject}\n")

# Mutation_ff77d0
    print(f"✅ {len(subjects)} subject(s) saved to {LOG_PATH}")
# Mutation_0adf86


if __name__ == '__main__':
    main()