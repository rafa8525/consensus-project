#!/usr/bin/env python3
"""
voice_gmail_handler.py
Version: 2.0
Purpose:
  Enables Gmail voice interaction using the permanent service-account key.
  Supports:
    • Reading and summarizing recent emails
    • Voice-based queries like "Read my latest email" or "Summarize my inbox"
"""

import datetime
import traceback
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2 import service_account

# === PATHS ===
BASE = Path("/home/rafa1215/consensus-project")
SERVICE_FILE = BASE / "memory/system/service_account.json"   # fixed path
LOG_FILE = BASE / "memory/logs/email/voice_gmail_handler.log"

# === SCOPES ===
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# === LOGGING ===
def log(message: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

# === BUILD GMAIL SERVICE ===
def get_gmail_service():
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_FILE, scopes=SCOPES
        )
        # Replace with your Gmail address for delegated access if needed
        delegated_creds = creds.with_subject("rafa5825@gmail.com")
        service = build("gmail", "v1", credentials=delegated_creds)
        return service
    except Exception as e:
        log(f"❌ Error building Gmail service: {e}")
        raise

# === READ LATEST EMAIL ===
def read_latest_email(max_results=1):
    try:
        service = get_gmail_service()
        log("🔍 Fetching latest email(s)...")

        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=max_results, labelIds=["INBOX"])
            .execute()
        )
        messages = results.get("messages", [])
        if not messages:
            log("📭 No new messages found.")
            return "No new messages were found."

        message_id = messages[0]["id"]
        msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()

        headers = msg["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown Sender)")
        snippet = msg.get("snippet", "")[:400]

        summary = f"Latest email from {sender} with subject '{subject}': {snippet}"
        log(f"✅ Retrieved: {summary}")
        return summary

    except Exception as e:
        log(f"❌ Error while reading Gmail: {e}\n{traceback.format_exc()}")
        return "An error occurred while accessing Gmail."

# === HANDLE VOICE COMMAND ===
def handle_voice_command(command: str):
    log(f"🎤 Voice command received: {command}")
    command_lower = command.lower()

    if "latest email" in command_lower or "read my email" in command_lower:
        return read_latest_email()
    elif "summarize" in command_lower or "email summary" in command_lower:
        return read_latest_email(3)
    else:
        msg = "Command not recognized for Gmail voice handler."
        log(msg)
        return msg

# === MAIN (manual test) ===
if __name__ == "__main__":
    print(handle_voice_command("Read my latest email"))
