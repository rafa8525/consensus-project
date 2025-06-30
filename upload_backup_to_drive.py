import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load .env file
from dotenv import load_dotenv
load_dotenv()

TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"
BACKUP_FILE = "/tmp/secure_logs_2025-06-26.zip"

# Check token file
if not Path(TOKEN_PATH).exists():
    raise FileNotFoundError("token.json is missing.")

# Load credentials
creds = Credentials.from_authorized_user_file(TOKEN_PATH)

# Build service
service = build("drive", "v3", credentials=creds)

# Upload
file_metadata = {"name": os.path.basename(BACKUP_FILE)}
media = MediaFileUpload(BACKUP_FILE, mimetype="application/zip", resumable=True)

try:
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"✅ Backup uploaded to Drive successfully. File ID: {file.get('id')}")
except Exception as e:
    print(f"❌ Drive upload failed: {e}")
