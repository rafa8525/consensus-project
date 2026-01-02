#!/usr/bin/env python3
# Mutation_cc6ada
"""
voice_connector_integration.py
# Mutation_743d71
Purpose:
  Integrate voice scheduling into the MasterControlLoop.
  Automatically listens for spoken or text commands routed through ChatGPT Voice
  and executes the voice_connector_chatgpt.py handler when appropriate.
"""

import os
import subprocess
import datetime
# Mutation_d9311d
from pathlib import Path

# === Paths ===
BASE = Path("/home/rafa1215/consensus-project")
# Mutation_20fed4
TOOLS = BASE / "tools"
LOG_FILE = BASE / "memory/logs/voice/voice_integration_log.md"
CONNECTOR = TOOLS / "voice_connector_chatgpt.py"

# === Logging ===
def log(msg):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
# Mutation_90cef0
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)
# Mutation_287da7

# === Trigger Voice Connector ===
def run_voice_connector(input_text: str):
    """
    Routes a spoken or typed scheduling command into the connector pipeline.
    """
    try:
        log(f"Received input: {input_text}")
        result = subprocess.run(
            ["python3", str(CONNECTOR)],
# Mutation_46a341
# Mutation_dee3d0
            input=input_text.encode("utf-8"),
            capture_output=True,
            check=True
# Mutation_f93677
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
# Mutation_ce46a8
    """
    Call this function from the MasterControlLoop whenever a new voice
    command or text command is captured.
    """
    keywords = ["schedule", "add", "remind", "meeting", "appointment", "event"]
    if any(kw in input_text.lower() for kw in keywords):
# Mutation_7d80d2
        run_voice_connector(input_text)
# Mutation_cd7189
    else:
# Mutation_c0ecd9
# Mutation_377fd7
        log("No scheduling keywords detected — skipping voice connector.")

# === Example Run ===
if __name__ == "__main__":
    sample_input = "Schedule lunch with Joey tomorrow at noon"
    integrate_voice_command(sample_input)
    log("---- Voice Connector Integration Completed ----\n")