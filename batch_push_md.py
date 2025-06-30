
import os
import requests
import base64
import sys

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("Missing GITHUB_TOKEN environment variable")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

repo = "rafa8525/consensus-project"
branch = "v1.1-dev"

# Command-line arguments
if len(sys.argv) != 3:
    print("Usage: python batch_push_md.py <local_file_path> <remote_repo_path>")
    print("Example: python batch_push_md.py logs/daily_log.md memory/logs/daily_log.md")
    sys.exit(1)

file_path = sys.argv[1]
remote_path = sys.argv[2]

# Read local file
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()
encoded_content = base64.b64encode(content.encode()).decode()

# Step 1: Get existing SHA if file already in GitHub
sha = None
url = f"https://api.github.com/repos/{repo}/contents/{remote_path}?ref={branch}"
sha_response = requests.get(url, headers=headers)
if sha_response.status_code == 200:
    sha = sha_response.json().get("sha")

# Step 2: Prepare payload
payload = {
    "message": f"🔄 Auto-upload or update {os.path.basename(remote_path)} via batch uploader",
    "branch": branch,
    "content": encoded_content
}
if sha:
    payload["sha"] = sha

# Step 3: Upload via PUT
put_url = f"https://api.github.com/repos/{repo}/contents/{remote_path}"
put_response = requests.put(put_url, headers=headers, json=payload)

if put_response.status_code in [200, 201]:
    print(f"✅ {remote_path} successfully pushed.")
else:
    print(f"❌ Upload failed: {put_response.status_code}")
    print(put_response.json())
