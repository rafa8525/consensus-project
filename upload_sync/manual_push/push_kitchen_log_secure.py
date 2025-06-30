
import os
import requests

# Load GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("Missing GITHUB_TOKEN environment variable")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Set your GitHub details
repo = "rafa8525/consensus-project"
branch = "v1.1-dev"
path = "memory/logs/geofencing/kitchen_log.md"
file_path = "upload_sync/manual_push/kitchen_log.md"
commit_message = "🍽️ Add kitchen_log.md via GitHub API (secured)"

# Read the local file content
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

import base64
encoded_content = base64.b64encode(content.encode()).decode()

# Construct the API URL
url = f"https://api.github.com/repos/{repo}/contents/{path}"

# Construct the JSON payload
payload = {
    "message": commit_message,
    "branch": branch,
    "content": encoded_content
}

# Make the request to upload the file
response = requests.put(url, headers=headers, json=payload)

if response.status_code in [200, 201]:
    print("✅ kitchen_log.md successfully uploaded.")
else:
    print(f"❌ Upload failed: {response.status_code}")
    print(response.json())
