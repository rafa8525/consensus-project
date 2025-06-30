import base64
import requests

# === Replace this with your actual token ===
token = "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"

# File prep
with open("kitchen_log.md", "rb") as f:
    content = base64.b64encode(f.read()).decode()

# GitHub config
url = "https://api.github.com/repos/rafa8525/consensus-project/contents/memory/logs/geofencing/kitchen_log.md"
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}
payload = {
    "message": "Add kitchen_log.md via GitHub API",
    "content": content,
    "branch": "v1.1-dev"
}

# Push it!
res = requests.put(url, headers=headers, json=payload)
print("✅ Success!" if res.status_code in [200, 201] else f"❌ Failed: {res.status_code}\n{res.text}")
