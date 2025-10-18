#!/usr/bin/env python3
"""
gmail_misc_sorter.py
Scans the Gmail label 'Misc' and sorts all messages by sender.
Part of the AI Consensus System Gmail management suite.
"""

import os
import datetime
from collections import defaultdict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime

# === CONFIG ===
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]
TOKEN_FILE = os.path.expanduser(
    "~/consensus-project/memory/core/secrets/token_gmail.json"
)
OUTPUT_LOG = os.path.expanduser(
    "~/consensus-project/memory/logs/email/misc_sorted_by_sender.md"
)
TARGET_LABEL = "Misc"  # Label to scan
MAX_MESSAGES = 50  # Adjust as needed


def load_credentials():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError("Missing Gmail token. Run gmail_auth_setup.py first.")
    return Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)


def find_label_id(service, label_name):
    """Get the Gmail API label ID for a given label name."""
    results = service.users().labels().list(userId="me").execute()
    for label in results.get("labels", []):
        if label["name"].lower() == label_name.lower():
            return label["id"]
    return None


def fetch_messages_by_label(service, label_id, max_results=MAX_MESSAGES):
    """Fetch message metadata under a specific label ID."""
    results = service.users().messages().list(
        userId="me", labelIds=[label_id], maxResults=max_results
    ).execute()
    return results.get("messages", [])


def get_message_details(service, message_id):
    """Extract sender, subject, date, and snippet from a Gmail message."""
    m = service.users().messages().get(userId="me", id=message_id).execute()
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

    try:
        dt = parsedate_to_datetime(date_str)
        date_fmt = dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        date_fmt = date_str

    return sender, subject, snippet, date_fmt


def main():
    creds = load_credentials()
    service = build("gmail", "v1", credentials=creds)

    print(f"🔍 Searching for label '{TARGET_LABEL}'...")
    label_id = find_label_id(service, TARGET_LABEL)
    if not label_id:
        print(f"⚠️ Label '{TARGET_LABEL}' not found in Gmail.")
        return

    print(f"📂 Found label ID: {label_id}")
    messages = fetch_messages_by_label(service, label_id)
    if not messages:
        print(f"No messages found under '{TARGET_LABEL}'.")
        return

    print(f"📬 Retrieved {len(messages)} messages from '{TARGET_LABEL}'.")

    # Group by sender
    grouped = defaultdict(list)
    for msg in messages:
        sender, subject, snippet, date_fmt = get_message_details(service, msg["id"])
        grouped[sender].append((subject, snippet, date_fmt))

    # Sort senders alphabetically
    sorted_senders = sorted(grouped.keys(), key=lambda s: s.lower())

    # Write to file
    os.makedirs(os.path.dirname(OUTPUT_LOG), exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
        f.write(f"# Misc Folder – Sorted by Sender ({ts})\n\n")
        for sender in sorted_senders:
            f.write(f"## {sender}\n")
            for subject, snippet, date_fmt in grouped[sender]:
                f.write(f"- **{subject}** ({date_fmt})\n  Snippet: {snippet}\n")
            f.write("\n")

    print(f"✅ Misc folder sorted successfully.")
    print(f"📄 Output saved to: {OUTPUT_LOG}")


if __name__ == "__main__":
    main()
