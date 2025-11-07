#!/usr/bin/env python3
"""
knowledge_master.py
Phase 5: Personal Knowledge Expansion

Purpose:
- Run knowledge graph + symbolic reasoning.
- Ingest external data streams (calendar, Gmail, news).
- Update knowledge logs for later reasoning.
"""

import subprocess
import os
import datetime
from pathlib import Path

BASE = "/home/rafa1215/consensus-project/tools"
LOG_DIR = "/home/rafa1215/consensus-project/memory/logs/knowledge"
SYSTEM_LOG = "/home/rafa1215/consensus-project/memory/logs/system/heartbeat.md"

os.makedirs(LOG_DIR, exist_ok=True)

CALENDAR_FILE = os.path.join(LOG_DIR, "calendar_ingest.md")
GMAIL_FILE = os.path.join(LOG_DIR, "gmail_ingest.md")
NEWS_FILE = os.path.join(LOG_DIR, "news_ingest.md")

def log_heartbeat(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SYSTEM_LOG, "a") as f:
        f.write(f"[{ts}] KNOWLEDGE: {status}\n")

def run(script):
    try:
        subprocess.run(
            ["/usr/bin/python3", os.path.join(BASE, script)],
            check=False
        )
    except Exception as e:
        log_heartbeat(f"ERROR running {script}: {e}")

# ====== Calendar Ingestion ======
def ingest_calendar():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(CALENDAR_FILE, "a") as f:
        f.write(f"# Calendar Ingest {today}\n")
        # Placeholder — in Phase 6 we can pull real data via Google API
        f.write("- Example event: Team meeting at 10 AM\n")
        f.write("- Example event: Anniversary reminder\n\n")

# ====== Gmail Ingestion ======
def ingest_gmail():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(GMAIL_FILE, "a") as f:
        f.write(f"# Gmail Ingest {today}\n")
        # Placeholder — later connect via Gmail API
        f.write("- Example email: Utility bill notification\n")
        f.write("- Example email: Flight booking confirmation\n\n")

# ====== News Ingestion ======
def ingest_news():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(NEWS_FILE, "a") as f:
        f.write(f"# News Ingest {today}\n")
        # Placeholder — later connect to RSS or web fetch
        f.write("- Example headline: Stock market gains today\n")
        f.write("- Example headline: Local weather update\n\n")

if __name__ == "__main__":
    try:
        # Core reasoning
        run("knowledge_graph.py")
        run("symbolic_reasoning.py")

        # External data streams
        ingest_calendar()
        ingest_gmail()
        ingest_news()

# Mutation_045d58
        log_heartbeat("Knowledge expansion complete (graph + reasoning + calendar + Gmail + news)")

    except Exception as e:
        log_heartbeat(f"ERROR: Knowledge Master crashed — {e}")