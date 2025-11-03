#!/usr/bin/env python3
"""
gmail_alert_agent.py
Scans unread Gmail messages for urgent keywords and triggers immediate alerts.

Integrated with AI Consensus System:
- Pulls unread Gmail using saved OAuth token
- Checks for critical keywords (PG&E, invoice, security, OpenAI alert)
- Logs alerts
- Triggers immediate voice or SMS notification via Twilio
"""

import os
import datetime
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime
import subprocess

# === CONFIG ===
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]
TOKEN_FILE = os.path.expanduser(
    "/home/rafa1215/.secrets/google/token_gmail.json"
)
ALERT_LOG = os.path.expanduser(
    "~/consensus-project/memory/logs/email/urgent_alerts.md"
)

# === ALERT KEYWORDS ===
URGENT_KEYWORDS = ["pge", "pg&e", "invoice", "security", "openai alert"]

# === OPTIONAL: SMS CONFIG (using Twilio) ===
TWILIO_ENABLED = True
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER", "")
TWILIO_TO = os.getenv("TWILIO_TO_NUMBER", "")


def log_alert(subject, sender, date_str, snippet):
    """Append an urgent email alert to a log file."""
    os.makedirs(os.path.dirname(ALERT_LOG), exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = (
        f"\n\n## ⚠️ Urgent Gmail Alert – {ts}\n"
        f"**Subject:** {subject}\n"
        f"**From:** {sender}\n"
        f"**Date:** {date_str}\n"
        f"**Snippet:** {snippet}\n"
    )
    with open(ALERT_LOG, "a", encoding="utf-8") as f:
        f.write(entry)
    print(entry.strip())


def speak_alert(subject, sender):
    """Speak the alert aloud (placeholder for ChatGPT Voice or TTS)."""
    text = f"Urgent email alert. Subject: {subject}. From: {sender}."
    print(f"\n🗣 Speaking alert: {text}\n")

    # Example: integrate with your Pixel Watch / ChatGPT Voice / TTS
    # subprocess.run(["say", text])  # macOS
    # subprocess.run(["espeak", text])  # Linux


def send_sms_alert(subject, sender):
    """Send SMS notification via Twilio."""
    if not (TWILIO_ENABLED and TWILIO_SID and TWILIO_TOKEN):
        print("Twilio not configured or disabled.")
        return

    from twilio.rest import Client
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        msg = f"URGENT EMAIL: {subject} from {sender}"
        client.messages.create(to=TWILIO_TO, from_=TWILIO_FROM, body=msg)
        print(f"📱 SMS alert sent: {msg}")
    except Exception as e:
        print(f"⚠️ Error sending SMS: {e}")


def fetch_unread_emails(service):
    """Fetch unread Gmail messages."""
    results = service.users().messages().list(
        userId="me", labelIds=["UNREAD"], maxResults=20
    ).execute()
    return results.get("messages", [])


def check_for_urgent_keywords(service):
    """Scan unread messages for urgent keywords."""
    messages = fetch_unread_emails(service)
    alerts_found = 0

    for msg in messages:
        m = service.users().messages().get(userId="me", id=msg["id"]).execute()
        payload = m.get("payload", {})
        headers = payload.get("headers", [])
        snippet = m.get("snippet", "(no preview)")
        subject = sender = date_str = "?"
        for h in headers:
            name = h.get("name", "").lower()
            if name == "subject":
                subject = h.get("value", "")
            elif name == "from":
                sender = h.get("value", "")
            elif name == "date":
                date_str = h.get("value", "")

        # Combine searchable text
        combined = f"{subject} {snippet}".lower()
        if any(word in combined for word in URGENT_KEYWORDS):
            log_alert(subject, sender, date_str, snippet)
            speak_alert(subject, sender)
            send_sms_alert(subject, sender)
            alerts_found += 1

    if alerts_found == 0:
        print("No urgent emails detected.")
    else:
        print(f"✅ {alerts_found} urgent email(s) detected and processed.")


def main():
    """Main alert-check routine."""
    if not os.path.exists(TOKEN_FILE):
        print("Missing Gmail token. Run gmail_auth_setup.py first.")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build("gmail", "v1", credentials=creds)

    print("🔍 Checking Gmail for urgent keywords...")
    check_for_urgent_keywords(service)


if __name__ == "__main__":
    main()
