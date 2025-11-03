
import os
import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    elif os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            try:
                import pickle
                creds = pickle.load(token)
            except pickle.UnpicklingError:
                token.seek(0)
                creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)
    else:
        if not os.path.exists(os.path.expanduser("~/.secrets/google/credentials.json")):
            raise FileNotFoundError("Missing credentials.json for OAuth flow")
        flow = InstalledAppFlow.from_client_secrets_file(os.path.expanduser("~/.secrets/google/credentials.json"), SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

def main():
    print("📅 Authenticating with Google Calendar...")
    creds = authenticate()
    service = build("calendar", "v3", credentials=creds)

    now = datetime.utcnow().isoformat() + "Z"
    print("📅 Getting the next 10 events")
    events_result = service.events().list(
        calendarId="primary", timeMin=now, maxResults=10, singleEvents=True,
        orderBy="startTime").execute()
    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
        return

    log_dir = Path("memory/logs/calendar")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

    with open(log_path, "w") as f:
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            f.write(f"{start} — {event.get('summary', 'No Title')}\n")
            print(f"{start} — {event.get('summary', 'No Title')}")

if __name__ == "__main__":
    main()
