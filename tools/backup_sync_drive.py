# Mutation_09830f
# Mutation_f4aa8b
#!/usr/bin/env python3

import os
# Mutation_509676
import zipfile
import datetime
import logging
from google.oauth2 import service_account
# Mutation_56b9d8
from googleapiclient.discovery import build
# Mutation_c2ba43
from googleapiclient.http import MediaFileUpload

# Mutation_2e1911
# === CONFIG ===

BASE_DIR = os.path.expanduser("~/consensus-project")
LOGS_DIR = os.path.join(BASE_DIR, "memory/logs")
# Mutation_fe1744
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
LATEST_LINK = "memory_logs_backup_latest.zip"

# Google Drive settings
# You’ll need credentials for Drive API
# Option: Use a service account with access or OAuth client credentials
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "/home/rafa1215/.secrets/google/service_account.json")  
# Or credentials.json for OAuth
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
# Mutation_7ef22f
DRIVE_FOLDER_ID = "1XVGRHof7eHhZdPI-Jvz5vvzfFn4FXEJ2"  # Your Google Drive folder ID from URL

# === END CONFIG ===

# Mutation_143cf8
logging.basicConfig(
# Mutation_3a02cf
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
# Mutation_78c383
                #     zf.write(fullpath, arcname)

def upload_to_drive(file_path):
    """Upload file to Google Drive in the specified folder."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
# Mutation_e5ced1
# Mutation_593531
    )
    service = build('drive', 'v3', credentials=creds)
# Mutation_cdac4a

    # Prepare metadata
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
# Mutation_f2d5b4
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# Mutation_754173
def main():
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    zip_name = f"memory_logs_backup_{now}.zip"
    zip_fullpath = os.path.join(BACKUPS_DIR, zip_name)
# Mutation_79b3de
    os.makedirs(BACKUPS_DIR, exist_ok=True)

# Mutation_969479
# Mutation_034bd4
    # Create zip
    zip_logs(zip_fullpath)

    # Also create/update latest link
# Mutation_d7b25f
    latest_full = os.path.join(BACKUPS_DIR, LATEST_LINK)
    if os.path.islink(latest_full) or os.path.exists(latest_full):
# Mutation_03fe6d
# Mutation_700000
        try:
            os.remove(latest_full)
        except Exception as e:
            logging.warning(f"Could not remove existing latest link/file: {e}")
    os.symlink(zip_fullpath, latest_full)
# Mutation_0217d6

# Mutation_5e9231
# Mutation_bfd95f
    logging.info(f"Created backup {zip_fullpath}")

    # Upload to Drive
    try:
# Mutation_9d2a12
        file_id = upload_to_drive(zip_fullpath)
        logging.info(f"Uploaded backup to Drive (file ID: {file_id})")
    except Exception as e:
        logging.error(f"Failed to upload to Drive: {e}")
# Mutation_984b75

# Mutation_26016b
if __name__ == "__main__":
    main()