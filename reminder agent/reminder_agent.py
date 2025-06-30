import os
import pickle
import datetime
import pytz
import requests

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ---- CONFIG ----
SHEET_ID = '1Xn8GB_GITJmU1f4kcJ7mdsvuz6zGoo2oFU8_YxkwGAQ'  # Your sheet ID (from your link)
RANGE_NAME = 'Sheet1!A2:G'  # Data rows (skip headers)
TIMEZONE = 'America/Los_Angeles'  # Set to your timezone
CHECK_INTERVAL_MINUTES = 10        # How often script runs (for escalation)
SMS_WEBHOOK_URL = "https://rafa1215.pythonanywhere.com/send_sms"
WEBHOOK_SECRET = "Maribelasia1!"   # Your webhook secret

# ---- Google Sheets Auth ----
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_creds():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def send_sms(message):
    payload = {
        "message": message,
        "secret": WEBHOOK_SECRET
    }
    try:
        r = requests.post(SMS_WEBHOOK_URL, json=payload)
        return r.status_code == 200
    except Exception as e:
        print("Failed to send SMS:", e)
        return False

def main():
    creds = get_creds()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])

    tz = pytz.timezone(TIMEZONE)
    now = datetime.datetime.now(tz)

    updates = []
    for idx, row in enumerate(rows):
        # Unpack columns
        reminder = (row + ['']*7)[:7]
        name, due_time, repeat, status, last_notified, escalate, notes = reminder

        # Parse due time
        try:
            due_dt = tz.localize(datetime.datetime.strptime(due_time.strip(), "%Y-%m-%d %H:%M"))
        except Exception:
            continue  # Skip if bad date

        # Check if pending and due/overdue
        if status.lower().strip() == 'pending':
            # Parse last_notified
            notified_dt = None
            if last_notified.strip():
                try:
                    notified_dt = tz.localize(datetime.datetime.strptime(last_notified.strip(), "%Y-%m-%d %H:%M"))
                except Exception:
                    pass

            # Escalation (in minutes)
            escalate_min = 0
            if escalate.strip():
                try:
                    if 'hour' in escalate:
                        escalate_min = int(escalate.split()[0]) * 60
                    elif 'min' in escalate:
                        escalate_min = int(escalate.split()[0])
                except Exception:
                    escalate_min = 0

            # Check if needs notification
            needs_notify = False
            if now >= due_dt:
                if not notified_dt:
                    needs_notify = True
                else:
                    # If escalation interval passed, repeat SMS
                    if (now - notified_dt).total_seconds() >= escalate_min * 60:
                        needs_notify = True

            if needs_notify:
                msg = f"Reminder: {name} (Due: {due_time}). Notes: {notes}"
                if send_sms(msg):
                    # Update Last Notified to now
                    updates.append((idx+2, now.strftime("%Y-%m-%d %H:%M")))

    # Write updates back to Sheet
    if updates:
        data = []
        for rownum, ts in updates:
            data.append({
                'range': f'Sheet1!E{rownum}',
                'values': [[ts]]
            })
        body = {'valueInputOption': 'RAW', 'data': data}
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID, body=body).execute()

if __name__ == '__main__':
    main()
