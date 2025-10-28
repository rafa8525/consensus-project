#!/usr/bin/env python3
"""
voice_connector_chatgpt.py
Purpose:
  Enables ChatGPT Voice to call the voice_schedule_event.py script automatically.
  Any voice command containing "schedule", "add", or "remind" will be parsed
  and forwarded to the event creator to generate a real Google Calendar event.
"""

import subprocess
import datetime
from pathlib import Path

# === Paths ===
BASE = Path("/home/rafa1215/consensus-project")
VOICE_SCHEDULER = BASE / "tools/voice_schedule_event.py"
LOG_FILE = BASE / "memory/logs/calendar/voice_connector_log.md"

# === Logging helper ===
def log(msg):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

# === Command filter ===
def is_schedule_command(text: str):
    keywords = ["schedule", "add", "remind", "appointment", "meeting", "event"]
    return any(kw in text.lower() for kw in keywords)

# === Execute scheduling ===
def handle_voice_input(voice_text: str):
    log(f"Received voice command: {voice_text}")
    if not is_schedule_command(voice_text):
        log("Not a scheduling command — ignored.")
        return

    try:
        subprocess.run(
            ["python3", str(VOICE_SCHEDULER)],
            input=voice_text.encode("utf-8"),
            capture_output=True,
            check=True,
        )
        log(f"✅ Forwarded to voice_schedule_event.py: {voice_text}")
    except subprocess.CalledProcessError as e:
        log(f"❌ Error running scheduler: {e.stderr.decode(errors='ignore')}")
    except Exception as e:
        log(f"❌ Unexpected failure: {e}")

# === Example test ===
if __name__ == "__main__":
    # Simulate voice input (replace with your actual phrase)
    test_input = "Schedule dinner with Maribel on Saturday at 7 p.m."
    handle_voice_input(test_input)
    log("---- Voice Connector Completed ----\n")
