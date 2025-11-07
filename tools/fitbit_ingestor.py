#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Consensus System – Fitbit / Pixel Watch Ingestion Module
Author: Rafael / AI Consensus System
Purpose:
  • Pull Fitbit API health metrics (steps, sleep, heart-rate zones, weight)
  • Parse Pixel Watch data when locally available
  • Write normalized logs to memory/logs/fitness/ for analysis and reporting
"""

import os
import json
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
import requests

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

BASE_DIR = Path.home() / "consensus-project"
FITNESS_LOG_DIR = BASE_DIR / "memory/logs/fitness"
FITNESS_LOG_DIR.mkdir(parents=True, exist_ok=True)

SECRETS_DIR = BASE_DIR / "secrets"
TOKEN_FILE = SECRETS_DIR / "fitbit_token.json"
CLIENT_FILE = SECRETS_DIR / "fitbit_credentials.json"
SUMMARY_FILE = FITNESS_LOG_DIR / "fitbit_daily_summary.json"

FITBIT_BASE = "https://api.fitbit.com/1/user/-"
PIXEL_FILE = BASE_DIR / "memory/sensors/pixel_watch_data.json"

SYNC_INTERVAL = 6 * 3600  # every 6 hours

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log_line(msg: str):
    path = FITNESS_LOG_DIR / f"fitbit_ingestor_{datetime.now(timezone.utc).date()}.log"
    with open(path, "a") as f:
        f.write(f"[{timestamp()}] {msg}\n")
    print(msg)

def read_json(path: Path):
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {}

def write_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# --------------------------------------------------------------------------- #
# Fitbit Token Refresh
# --------------------------------------------------------------------------- #

def refresh_token():
    """Refresh Fitbit OAuth token using client credentials."""
    try:
        creds = read_json(CLIENT_FILE)
        token = read_json(TOKEN_FILE)
        if not creds or not token:
            log_line("❌ Fitbit credentials or token missing.")
            return None

        resp = requests.post(
            "https://api.fitbit.com/oauth2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": token["refresh_token"],
            },
            auth=(creds["client_id"], creds["client_secret"]),
        )
        resp.raise_for_status()
        new_token = resp.json()
        write_json(TOKEN_FILE, new_token)
        log_line("🔁 Fitbit access token refreshed.")
        return new_token["access_token"]
    except Exception as e:
        log_line(f"❌ Fitbit token refresh failed: {e}")
        return None

# --------------------------------------------------------------------------- #
# Fitbit Data Fetchers
# --------------------------------------------------------------------------- #

def get_fitbit_data(access_token: str, endpoint: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{FITBIT_BASE}/{endpoint}", headers=headers)
    resp.raise_for_status()
    return resp.json()

def collect_fitbit_summary(access_token: str):
    """Fetch key daily metrics."""
    today = datetime.now().strftime("%Y-%m-%d")
    summary = {}
    try:
        summary["steps"] = get_fitbit_data(access_token, f"activities/date/{today}.json").get("summary", {}).get("steps", 0)
        summary["sleep"] = get_fitbit_data(access_token, f"sleep/date/{today}.json").get("summary", {})
        summary["hr"] = get_fitbit_data(access_token, f"activities/heart/date/{today}/1d.json")
        summary["weight"] = get_fitbit_data(access_token, f"body/log/weight/date/{today}.json")
        log_line(f"✅ Fitbit data fetched for {today}: steps={summary['steps']}")
        return summary
    except Exception as e:
        log_line(f"❌ Fitbit fetch error: {e}")
        return {}

# --------------------------------------------------------------------------- #
# Pixel Watch Data Integration
# --------------------------------------------------------------------------- #

def collect_pixel_data():
    """Load locally logged Pixel Watch metrics if present."""
    if not PIXEL_FILE.exists():
        return {}
    try:
        data = read_json(PIXEL_FILE)
        log_line(f"📱 Pixel Watch data loaded ({len(data)} fields).")
        return data
    except Exception as e:
        log_line(f"⚠️ Pixel Watch read error: {e}")
        return {}

# --------------------------------------------------------------------------- #
# Normalization + Write
# --------------------------------------------------------------------------- #

def write_daily_summary(fitbit_data: dict, pixel_data: dict):
    combined = {
        "timestamp": timestamp(),
        "fitbit": fitbit_data,
        "pixel": pixel_data,
    }
    write_json(SUMMARY_FILE, combined)
    log_line(f"🧾 Daily fitness summary written ({SUMMARY_FILE.name}).")

# --------------------------------------------------------------------------- #
# Main Runner
# --------------------------------------------------------------------------- #

def main():
    log_line("=== Fitbit / Pixel Watch Ingestor Started ===")
    try:
        access_token = refresh_token()
        fitbit_data = collect_fitbit_summary(access_token) if access_token else {}
        pixel_data = collect_pixel_data()
        write_daily_summary(fitbit_data, pixel_data)
        log_line("💤 Entering passive mode (6 h intervals).")
        while True:
            time.sleep(SYNC_INTERVAL)
            access_token = refresh_token()
            fitbit_data = collect_fitbit_summary(access_token) if access_token else {}
            pixel_data = collect_pixel_data()
            write_daily_summary(fitbit_data, pixel_data)
    except KeyboardInterrupt:
        log_line("🛑 Fitbit / Pixel Watch Ingestor stopped manually.")
    except Exception:
        log_line(traceback.format_exc())

if __name__ == "__main__":
    main()
