import os
import datetime
import zipfile
import pyzipper
import base64
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Get secrets from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ZIP_PASSWORD = os.getenv("ZIP_PASSWORD")

if not GITHUB_TOKEN or not ZIP_PASSWORD:
    print("❌ Missing GITHUB_TOKEN or ZIP_PASSWORD in .env")
    exit(1)

today = datetime.date.today().isoformat()
ZIP_NAME = f"/tmp/secure_logs_{today}.zip"

FILES_TO_BACKUP = [
    "upload_sync/manual_push/kitchen_log.md",
    "upload_sync/manual_push/meal_log.md",
    "upload_sync/manual_push/heart_log.md",
    "upload_sync/manual_push/transit_log.md"
]

with pyzipper.AESZipFile(ZIP_NAME, 'w', compression=zipfile.ZIP_DEFLATED,
                         encryption=pyzipper.WZ_AES) as zf:
    zf.setpassword(ZIP_PASSWORD.encode())
    for file_path in FILES_TO_BACKUP:
        if os.path.exists(file_path):
            arcname = os.path.basename(file_path)
            zf.write(file_path, arcname=arcname)
        else:
            print(f"⚠️ File not found: {file_path}")

print(f"✅ Created encrypted ZIP: {ZIP_NAME}")

# Upload to GitHub
with open(ZIP_NAME, "rb") as f:
    content = base64.b64encode(f.read()).decode()

github_api_url = f"https://api.github.com/repos/rafa8525/consensus-project/contents/memory/backups/{os.path.basename(ZIP_NAME)}"
payload = {
    "message": f"Add encrypted backup for {today}",
    "content": content,
    "branch": "v1.1-dev"
}
headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
res = requests.put(github_api_url, json=payload, headers=headers)

if res.status_code in [200, 201]:
    print("✅ Backup uploaded to GitHub successfully.")
else:
    print("❌ GitHub upload failed:", res.status_code, res.json())
