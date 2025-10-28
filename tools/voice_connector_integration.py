#!/usr/bin/env python3
"""
voice_connector_integration.py
Purpose:
  Integrate voice scheduling into the MasterControlLoop.
  Automatically listens for spoken or text commands routed through ChatGPT Voice
  and executes the voice_connector_chatgpt.py handler when appropriate.
"""

import os
import subprocess
import datetime
from pathlib import Path

# === Paths ===
BASE = Path("/home/rafa1215/consensus-project")
TOOLS = BASE / "tools"
LOG_FILE = BASE / "memory/logs/voice/voice_integration_log.md"
CONNECTOR = TOOLS / "voice_connector_chatgpt.py"

# === Logging ===
def log(msg):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

# === Trigger Voice Connector ===
def run_voice_connector(input_text: str):
    """
    Routes a spoken or typed scheduling command into the connector pipeline.
    """
    try:
        log(f"Received input: {input_text}")
        result = subprocess.run(
            ["python3", str(CONNECTOR)],
            input=input_text.encode("utf-8"),
            capture_output=True,
            check=True
        )
        log(f"✅ Connector executed successfully for input: {input_text}")
        if result.stdout:
            log(result.stdout.decode(errors="ignore"))
    except subprocess.CalledProcessError as e:
        log(f"❌ Connector failed: {e.stderr.decode(errors='ignore')}")
    except Exception as e:
        log(f"❌ Unexpected error: {e}")

# === Integration Hook (for MasterControlLoop) ===
def integrate_voice_command(input_text: str):
    """
    Call this function from the MasterControlLoop whenever a new voice
    command or text command is captured.
    """
    keywords = ["schedule", "add", "remind", "meeting", "appointment", "event"]
    if any(kw in input_text.lower() for kw in keywords):
        run_voice_connector(input_text)
    else:
        log("No scheduling keywords detected — skipping voice connector.")

# === Example Run ===
if __name__ == "__main__":
    sample_input = "Schedule lunch with Joey tomorrow at noon"
    integrate_voice_command(sample_input)
    log("---- Voice Connector Integration Completed ----\n")
