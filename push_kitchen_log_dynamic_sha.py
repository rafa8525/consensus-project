
import os
import requests
import base64

# Load GitHub token from env
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
commit_message = "🔄 Update kitchen_log.md using live SHA"

# Step 1: Read local file
with open(file_path, "r", encoding="utf-8") as f:
    local_content = f.read()
encoded_content = base64.b64encode(local_content.encode()).decode()

# Step 2: Get the current SHA of the file on GitHub
url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
sha = None
sha_response = requests.get(url, headers=headers)
if sha_response.status_code == 200:
    sha = sha_response.json().get("sha")
elif sha_response.status_code == 404:
    sha = None  # file does not exist yet
else:
    print(f"❌ Could not get SHA: {sha_response.status_code}")
    print(sha_response.json())
    exit(1)

# Step 3: Construct payload
payload = {
    "message": commit_message,
    "branch": branch,
    "content": encoded_content
}
if sha:
    payload["sha"] = sha

# Step 4: Upload file (PUT)
upload_url = f"https://api.github.com/repos/{repo}/contents/{path}"
upload_response = requests.put(upload_url, headers=headers, json=payload)

if upload_response.status_code in [200, 201]:
    print("✅ kitchen_log.md uploaded or updated successfully.")
else:
    print(f"❌ Upload failed: {upload_response.status_code}")
    print(upload_response.json())
