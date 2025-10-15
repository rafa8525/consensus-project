#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Consensus System – Movie List Cloud Sync Agent
Author: Rafael / AI Consensus System
Purpose: Keep movie list synchronized with Google Drive (Google Sheets) and local backup.
"""

import os
import json
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

BASE_DIR = Path.home() / "consensus-project"
MEDIA_DIR = BASE_DIR / "memory/media"
LOG_DIR = BASE_DIR / "memory/logs/system/movie_sync"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOCAL_CACHE = MEDIA_DIR / "movies_backup.json"
CREDENTIALS_PATH = BASE_DIR / "secrets/google_credentials.json"
TOKEN_PATH = BASE_DIR / "secrets/google_token.json"
MOVIE_SHEET_ID = os.getenv("MOVIE_SHEET_ID")
MOVIE_SHEET_RANGE = os.getenv("MOVIE_SHEET_RANGE", "Movies!A2:B")  # default fallback
SYNC_INTERVAL = 6 * 3600  # 6 hours

# --------------------------------------------------------------------------- #
# Utility Functions
# --------------------------------------------------------------------------- #

def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(message: str):
    log_file = LOG_DIR / f"movie_sync_{datetime.now(timezone.utc).date()}.log"
    with open(log_file, "a") as f:
        f.write(f"[{timestamp()}] {message}\n")
    print(message)

def load_local_backup():
    if LOCAL_CACHE.exists():
        with open(LOCAL_CACHE, "r") as f:
            return json.load(f)
    return []

def save_local_backup(data):
    with open(LOCAL_CACHE, "w") as f:
        json.dump(data, f, indent=2)

# --------------------------------------------------------------------------- #
# Google Drive Sync
# --------------------------------------------------------------------------- #

def get_gdrive_service():
    """Build Google Sheets API service with token refresh."""
    try:
        creds = None
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                log("🔁 Google token refreshed successfully.")
            else:
                raise Exception("Google OAuth credentials invalid or missing.")
        return build("sheets", "v4", credentials=creds)
    except Exception as e:
        log(f"❌ Failed to initialize Google API service: {e}")
        return None

def pull_movies_from_cloud():
    """Fetch the latest movie list from Google Sheets."""
    service = get_gdrive_service()
    if not service or not MOVIE_SHEET_ID:
        log("⚠️ Cloud sync unavailable — using cached backup.")
        return load_local_backup()

    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=MOVIE_SHEET_ID,
            range=MOVIE_SHEET_RANGE
        ).execute()
        values = result.get("values", [])
        movies = [
            {"title": row[0], "notes": row[1] if len(row) > 1 else ""}
            for row in values
        ]
        save_local_backup(movies)
        log(f"✅ Synced {len(movies)} movies from Google Sheets.")
        return movies
    except Exception as e:
        log(f"❌ Cloud fetch failed: {e}")
        return load_local_backup()

def push_new_movie(title: str, notes: str = ""):
    """Add new movie entry both locally and to Google Sheets."""
    data = load_local_backup()
    new_entry = {"title": title, "notes": notes, "added_at": timestamp()}
    data.append(new_entry)
    save_local_backup(data)

    service = get_gdrive_service()
    if not service or not MOVIE_SHEET_ID:
        log(f"⚠️ Stored locally (no cloud access): {title}")
        return False

    try:
        sheet = service.spreadsheets()
        body = {"values": [[title, notes, timestamp()]]}
        sheet.values().append(
            spreadsheetId=MOVIE_SHEET_ID,
            range=MOVIE_SHEET_RANGE.split("!")[0] + "!A2",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()
        log(f"✅ Added '{title}' to Google Sheets successfully.")
        return True
    except Exception as e:
        log(f"❌ Cloud push failed: {e}")
        return False

# --------------------------------------------------------------------------- #
# Main Sync Loop
# --------------------------------------------------------------------------- #

def main():
    log("=== Movie Sync Agent Started ===")
    try:
        movies = pull_movies_from_cloud()
        log(f"🎬 Local movie list count: {len(movies)}")
        log(f"🗂 Using range: {MOVIE_SHEET_RANGE}")
        log("💤 Entering passive sync mode (6h intervals).")
        while True:
            time.sleep(SYNC_INTERVAL)
            pull_movies_from_cloud()
    except KeyboardInterrupt:
        log("🛑 Movie Sync Agent stopped manually.")
    except Exception:
        log(traceback.format_exc())

if __name__ == "__main__":
    main()
