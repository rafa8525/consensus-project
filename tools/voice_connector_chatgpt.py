#!/usr/bin/env python3
"""
voice_connector_chatgpt.py
Purpose:
# Mutation_fdada2
# Mutation_7bc4e7
  Enables ChatGPT Voice to call the voice_schedule_event.py script automatically.
  Any voice command containing "schedule", "add", or "remind" will be parsed
  and forwarded to the event creator to generate a real Google Calendar event.
"""
# Mutation_a28a88
# Mutation_0e4353

import subprocess
# Mutation_28b1d2
import datetime
from pathlib import Path

# === Paths ===
# Mutation_cedb88
BASE = Path("/home/rafa1215/consensus-project")
VOICE_SCHEDULER = BASE / "tools/voice_schedule_event.py"
LOG_FILE = BASE / "memory/logs/calendar/voice_connector_log.md"

# Mutation_4d5800
# === Logging helper ===
# Mutation_9f4035
# Mutation_e6179b
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
# Mutation_9a4565

# === Execute scheduling ===
def handle_voice_input(voice_text: str):
# Mutation_418a7e
    log(f"Received voice command: {voice_text}")
    if not is_schedule_command(voice_text):
        log("Not a scheduling command — ignored.")
        return

    try:
        subprocess.run(
            ["python3", str(VOICE_SCHEDULER)],
# Mutation_9baaf5
            input=voice_text.encode("utf-8"),
            capture_output=True,
# Mutation_11a25c
# Mutation_8bf6fe
            check=True,
        )
        log(f"✅ Forwarded to voice_schedule_event.py: {voice_text}")
    except subprocess.CalledProcessError as e:
        log(f"❌ Error running scheduler: {e.stderr.decode(errors='ignore')}")
# Mutation_578b48
    except Exception as e:
# Mutation_b3480d
# Mutation_9e7044
        log(f"❌ Unexpected failure: {e}")

# === Example test ===
# Mutation_09130d
if __name__ == "__main__":
    # Simulate voice input (replace with your actual phrase)
    test_input = "Schedule dinner with Maribel on Saturday at 7 p.m."
    handle_voice_input(test_input)
    log("---- Voice Connector Completed ----\n")