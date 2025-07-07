import base64
import time
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Setup paths and IDs ---
SHEET_ID = '1Xn8GB_GITJmU1f4kcJ7mdsvuz6zGoo2oFU8_YxkwGAQ'
SHEET_RANGE = 'Sheet1!A:G'
GMAIL_TOKEN = 'token.pickle'
GMAIL_CREDENTIALS = 'credentials.json'

# --- Load Gmail credentials ---
creds = Credentials.from_authorized_user_file(GMAIL_TOKEN, ['https://www.googleapis.com/auth/gmail.readonly'])
service = build('gmail', 'v1', credentials=creds)

# --- Load Google Sheets credentials ---
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
gs_creds = ServiceAccountCredentials.from_json_keyfile_name(GMAIL_CREDENTIALS, scope)
gc = gspread.authorize(gs_creds)
sheet = gc.open_by_key(SHEET_ID).sheet1

def get_new_reminders():
    results = service.users().messages().list(userId='me', q='is:unread').execute()
    messages = results.get('messages', [])
    new_tasks = []
    for msg in messages:
        msg_id = msg['id']
        msg_detail = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        headers = msg_detail['payload']['headers']
        subject = next((h['value'] for h in headers if h['name']=='Subject'), '')
        body = ''
        if 'data' in msg_detail['payload']['body']:
            body = base64.urlsafe_b64decode(msg_detail['payload']['body']['data']).decode('utf-8')
        else:
            parts = msg_detail['payload'].get('parts', [])
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        # Detect reminder
        if subject.lower().startswith('remind') or 'remind me' in body.lower():
            reminder = subject if subject.lower().startswith('remind') else body.strip()
            new_tasks.append((reminder, msg_id))
    return new_tasks

def add_reminder_to_sheet(reminder_text):
    now = time.strftime('%Y-%m-%d %H:%M')
    row = [reminder_text, now, "once", "pending", "", "", ""]
    sheet.append_row(row, value_input_option='RAW')

def mark_as_read(msg_id):
    service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()

if __name__ == "__main__":
    tasks = get_new_reminders()
    for reminder, msg_id in tasks:
        add_reminder_to_sheet(reminder)
        mark_as_read(msg_id)
        print(f"Added: {reminder}")

