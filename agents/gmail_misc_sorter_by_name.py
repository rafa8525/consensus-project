#!/usr/bin/env python3
"""
gmail_misc_sorter_by_name.py  – Auto-pagination edition
Scans all messages in Gmail label 'Misc' in 1 000-message pages.
Each batch is written as its own file and merged automatically.

Safe (read-only) – uses gmail.readonly scope only.
"""

import os
import datetime
from collections import defaultdict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime
import time

# === CONFIG ===
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]
TOKEN_FILE = os.path.expanduser("~/consensus-project/memory/core/secrets/token_gmail.json")
LOG_DIR = os.path.expanduser("~/consensus-project/memory/logs/email/")
TARGET_LABEL = "Misc"
BATCH_SIZE = 1000      # messages per page
SLEEP_BETWEEN_PAGES = 2  # seconds between Gmail API calls


def load_credentials():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError("Missing Gmail token. Run gmail_auth_setup.py first.")
    return Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)


def find_label_id(service, label_name):
    results = service.users().labels().list(userId="me").execute()
    for label in results.get("labels", []):
        if label["name"].lower() == label_name.lower():
            return label["id"]
    return None


def fetch_messages(service, label_id, page_token=None):
    """Fetch a single page of messages and return (messages, nextPageToken)."""
    results = service.users().messages().list(
        userId="me",
        labelIds=[label_id],
        maxResults=BATCH_SIZE,
        pageToken=page_token,
    ).execute()
    return results.get("messages", []), results.get("nextPageToken")


def get_message_details(service, message_id):
    """Extract sender, subject, snippet, date."""
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


def sort_batch(service, messages, batch_number):
    """Sort a batch alphabetically by sender and save to file."""
    grouped = defaultdict(list)
    for msg in messages:
        sender, subject, snippet, date_fmt = get_message_details(service, msg["id"])
        grouped[sender].append((subject, snippet, date_fmt))

    sorted_senders = sorted(grouped.keys(), key=lambda s: s.lower())

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file = os.path.join(LOG_DIR, f"misc_sorted_batch{batch_number}.md")
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Misc Folder – Batch {batch_number} Sorted Alphabetically ({ts})\n\n")
        for sender in sorted_senders:
            f.write(f"## {sender}\n")
            for subject, snippet, date_fmt in grouped[sender]:
                f.write(f"- **{subject}** ({date_fmt})\n  Snippet: {snippet}\n")
            f.write("\n")
    print(f"✅ Saved batch {batch_number}: {len(messages)} messages → {output_file}")
    return output_file


def merge_batches():
    """Merge all batch files into one combined file."""
    merged_path = os.path.join(LOG_DIR, "misc_sorted_merged.md")
    batch_files = sorted(
        [f for f in os.listdir(LOG_DIR) if f.startswith("misc_sorted_batch") and f.endswith(".md")]
    )
    lines = []
    for bf in batch_files:
        with open(os.path.join(LOG_DIR, bf), "r", encoding="utf-8") as f:
            lines.extend(f.readlines())
    with open(merged_path, "w", encoding="utf-8") as f:
        f.write("# Misc Folder – Merged Alphabetical Log\n\n")
        f.writelines(lines)
    print(f"📄 Merged {len(batch_files)} batch files → {merged_path}")


def main():
    creds = load_credentials()
    service = build("gmail", "v1", credentials=creds)

    label_id = find_label_id(service, TARGET_LABEL)
    if not label_id:
        print(f"⚠️ Label '{TARGET_LABEL}' not found.")
        return

    batch_number = 1
    page_token = None
    total_messages = 0

    while True:
        print(f"\n🔍 Fetching batch {batch_number} ...")
        messages, page_token = fetch_messages(service, label_id, page_token)
        if not messages:
            print("⚠️ No messages returned for this batch.")
            break

        total_messages += len(messages)
        sort_batch(service, messages, batch_number)

        if not page_token:
            print("✅ All pages retrieved.")
            break

        batch_number += 1
        time.sleep(SLEEP_BETWEEN_PAGES)

    merge_batches()
    print(f"✅ Completed sorting all pages. Total messages processed: {total_messages}")


if __name__ == "__main__":
    main()
