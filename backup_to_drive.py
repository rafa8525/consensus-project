#!/usr/bin/env python3
"""
backup_to_drive.py
Compress memory/logs/ and upload to Google Drive daily.
"""

import os
import json
import datetime
import zipfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# === CONFIG ===
LOGS_DIR = "memory/logs"
SYSTEM_LOG = "memory/logs/system/drive_backup_manifest.json"
BACKUP_DIR = "memory/backups"
DRIVE_FOLDER_ID = "1XVGRHof7eHhZdPI-Jvz5vvzfFn4FXEJ2"  # Your backup folder

# Path to your service account credentials JSON
SERVICE_ACCOUNT_FILE = os.path.expanduser("~/consensus-project/drive_service_account.json")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def make_zip(output_path):
    """Create a zip archive of memory/logs."""
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(LOGS_DIR):
            for f in files:
                if f.endswith(".py") or f.endswith(".gitignore"):
                    continue
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, LOGS_DIR)
                zf.write(full_path, arcname=rel_path)


def upload_to_drive(file_path, filename):
    """Upload the zip file to Google Drive."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)

    media = MediaFileUpload(file_path, mimetype="application/zip")

    file_metadata = {
        "name": filename,
        "parents": [DRIVE_FOLDER_ID]
    }

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return uploaded.get("id")


def update_manifest(ts, filename, file_id):
    os.makedirs(os.path.dirname(SYSTEM_LOG), exist_ok=True)
    entry = {
        "timestamp": ts,
        "filename": filename,
        "drive_file_id": file_id
    }

    if os.path.exists(SYSTEM_LOG):
        with open(SYSTEM_LOG, "r") as f:
            manifest = json.load(f)
    else:
        manifest = {"backups": []}

    manifest["backups"].append(entry)

    with open(SYSTEM_LOG, "w") as f:
        json.dump(manifest, f, indent=2)


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    filename = f"logs_backup_{ts}.zip"
    zip_path = os.path.join(BACKUP_DIR, filename)

    print(f"[backup] Creating ZIP {zip_path} ...")
    make_zip(zip_path)

    print(f"[backup] Uploading {filename} to Google Drive ...")
    file_id = upload_to_drive(zip_path, filename)

    print(f"[backup] Updating manifest {SYSTEM_LOG} ...")
    update_manifest(ts, filename, file_id)

    print("[backup] DONE.")


if __name__ == "__main__":
    main()
