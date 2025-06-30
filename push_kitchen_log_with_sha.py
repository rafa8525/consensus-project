
import os
import requests
import base64

# Load GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("Missing GITHUB_TOKEN environment variable")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

repo = "rafa8525/consensus-project"
branch = "v1.1-dev"
path = "memory/logs/geofencing/kitchen_log.md"
file_path = "upload_sync/manual_push/kitchen_log.md"
commit_message = "✏️ Overwrite kitchen_log.md using hardcoded SHA"

# Read file content
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()
encoded_content = base64.b64encode(content.encode()).decode()

# Use the known SHA
sha = "94062f35af326de85b3c6ccf8281da649d0c6dbb"

# Upload payload
payload = {
    "message": commit_message,
    "branch": branch,
    "content": encoded_content,
    "sha": sha
}

# GitHub API URL
url = f"https://api.github.com/repos/{repo}/contents/{path}"

# Perform PUT request
response = requests.put(url, headers=headers, json=payload)

if response.status_code in [200, 201]:
    print("✅ kitchen_log.md successfully updated with hardcoded SHA.")
else:
    print(f"❌ Upload failed: {response.status_code}")
    print(response.json())
