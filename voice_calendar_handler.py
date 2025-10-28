# /home/rafa1215/consensus-project/voice_calendar_handler.py

import datetime
import traceback
from pathlib import Path
from calendar_utils import get_calendar_service

BASE = Path("/home/rafa1215/consensus-project")
LOG_FILE = BASE / "memory/logs/calendar/voice_calendar_handler.log"

def log(msg: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

def get_next_event():
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + "Z"
        log("📅 Querying next upcoming calendar event...")

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=1,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        if not events:
            return "You have no upcoming events."

        event = events[0]
        start = event["start"].get("dateTime", event["start"].get("date"))
        summary = event.get("summary", "(No title)")
        response = f"Next event: '{summary}' at {start}."
        log(f"✅ {response}")
        return response

    except Exception as e:
        log(f"❌ Calendar fetch failed: {e}\n{traceback.format_exc()}")
        return "I couldn't access your calendar right now."

def handle_voice_command(command: str):
    log(f"🎤 Voice command received: {command}")
    cmd = command.lower()
    if "next event" in cmd or "calendar" in cmd:
        return get_next_event()
    else:
        return "Command not recognized for calendar voice handler."

if __name__ == "__main__":
    print(handle_voice_command("What’s my next calendar event?"))
