
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
commit_message = "🔄 Update kitchen_log.md via GitHub API (with SHA check)"

# Read file content
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

encoded_content = base64.b64encode(content.encode()).decode()

# GitHub API URL
url = f"https://api.github.com/repos/{repo}/contents/{path}"

# Step 1: Check if the file exists and fetch the SHA
response = requests.get(url, headers=headers)
if response.status_code == 200:
    sha = response.json()["sha"]
else:
    sha = None

# Step 2: Construct the payload
payload = {
    "message": commit_message,
    "branch": branch,
    "content": encoded_content
}
if sha:
    payload["sha"] = sha

# Step 3: Upload or update the file
put_response = requests.put(url, headers=headers, json=payload)

if put_response.status_code in [200, 201]:
    print("✅ kitchen_log.md successfully uploaded or updated.")
else:
    print(f"❌ Upload failed: {put_response.status_code}")
    print(put_response.json())
