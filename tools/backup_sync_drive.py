#!/usr/bin/env python3

import os
import zipfile
import datetime
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === CONFIG ===

BASE_DIR = os.path.expanduser("~/consensus-project")
LOGS_DIR = os.path.join(BASE_DIR, "memory/logs")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
LATEST_LINK = "memory_logs_backup_latest.zip"

# Google Drive settings
# You’ll need credentials for Drive API
# Option: Use a service account with access or OAuth client credentials
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "google_credentials.json")  
# Or credentials.json for OAuth
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DRIVE_FOLDER_ID = "1XVGRHof7eHhZdPI-Jvz5vvzfFn4FXEJ2"  # Your Google Drive folder ID from URL

# === END CONFIG ===

logging.basicConfig(
    filename=os.path.join(BASE_DIR, "memory/logs/scheduler/backup_drive.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def zip_logs(zip_path):
    """Make a zip of LOGS_DIR, excluding runtime logs but including .keep placeholders."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(LOGS_DIR):
            for file in files:
                if file == ".keep":
                    fullpath = os.path.join(root, file)
                    arcname = os.path.relpath(fullpath, BASE_DIR)
                    zf.write(fullpath, arcname)
                # optionally include stable summary files (.md/.json) if you want
                # elif file.endswith(".md") or file.endswith(".json"):
                #     fullpath = os.path.join(root, file)
                #     arcname = os.path.relpath(fullpath, BASE_DIR)
                #     zf.write(fullpath, arcname)

def upload_to_drive(file_path):
    """Upload file to Google Drive in the specified folder."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=creds)

    # Prepare metadata
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def main():
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    zip_name = f"memory_logs_backup_{now}.zip"
    zip_fullpath = os.path.join(BACKUPS_DIR, zip_name)
    os.makedirs(BACKUPS_DIR, exist_ok=True)

    # Create zip
    zip_logs(zip_fullpath)

    # Also create/update latest link
    latest_full = os.path.join(BACKUPS_DIR, LATEST_LINK)
    if os.path.islink(latest_full) or os.path.exists(latest_full):
        try:
            os.remove(latest_full)
        except Exception as e:
            logging.warning(f"Could not remove existing latest link/file: {e}")
    os.symlink(zip_fullpath, latest_full)

    logging.info(f"Created backup {zip_fullpath}")

    # Upload to Drive
    try:
        file_id = upload_to_drive(zip_fullpath)
        logging.info(f"Uploaded backup to Drive (file ID: {file_id})")
    except Exception as e:
        logging.error(f"Failed to upload to Drive: {e}")

if __name__ == "__main__":
    main()
