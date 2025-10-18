#!/usr/bin/env python3
"""
gmail_agent.py
Fetches and summarizes unread Gmail messages automatically.
Runs on a 30-minute schedule or by voice command.
"""

import os
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime

# === Config ===
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]
TOKEN_FILE = os.path.expanduser(
    "~/consensus-project/memory/core/secrets/token_gmail.json"
)
LOG_FILE = os.path.expanduser(
    "~/consensus-project/memory/logs/email/daily_summary.md"
)
MAX_MESSAGES = 10  # how many unread messages to summarize


def load_credentials():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(
            f"Missing Gmail token at {TOKEN_FILE}. Run gmail_auth_setup.py first."
        )
    return Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)


def fetch_unread_messages(service, max_results=MAX_MESSAGES):
    """Return a list of unread message metadata."""
    results = service.users().messages().list(
        userId="me", labelIds=["UNREAD"], maxResults=max_results
    ).execute()
    messages = results.get("messages", [])
    summaries = []

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

        # Parse date nicely
        try:
            dt = parsedate_to_datetime(date_str)
            date_fmt = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            date_fmt = date_str

        summaries.append(
            f"- **{subject}**\n  From: {sender}\n  Date: {date_fmt}\n  Snippet: {snippet}\n"
        )

    return summaries


def write_summary(summaries):
    """Append summaries to log file."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n\n## Gmail Summary – {ts}\n")
        if not summaries:
            f.write("No unread messages.\n")
        else:
            f.write("\n".join(summaries))
    print(f"✅ Log updated: {LOG_FILE}")


def main():
    creds = load_credentials()
    service = build("gmail", "v1", credentials=creds)
    summaries = fetch_unread_messages(service)
    write_summary(summaries)
    if summaries:
        print(f"Fetched and logged {len(summaries)} unread messages.")
    else:
        print("No unread messages found.")


if __name__ == "__main__":
    main()
