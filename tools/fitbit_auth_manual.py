#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fitbit OAuth 2.0 Manual Authorization
Author: Rafael / AI Consensus System
Purpose: Generate Fitbit access + refresh tokens without SDK issues.
"""

import requests
import urllib.parse

# Fitbit app credentials
CLIENT_ID = "23TGJY"
CLIENT_SECRET = "d4f8c845d7dc75c44d5bf5088477180"
REDIRECT_URI = "https://localhost/"

# Step 1: Guide user to login
AUTH_URL = (
    "https://www.fitbit.com/oauth2/authorize?"
    + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "activity nutrition heartrate location profile settings sleep weight",
        "prompt": "login"
    })
)

print("\n🔗 Go to this URL in your browser to authorize your Fitbit app:\n")
print(AUTH_URL)
print("\nAfter approving access, you’ll be redirected to:")
print("https://localhost/?code=YOUR_CODE_HERE\n")

# Step 2: Paste the code
code = input("👉 Paste the value that appears after 'code=' from the URL: ").strip()
code = code.split("&")[0]  # Remove state or trailing markers

# Step 3: Exchange for token
print("\n🔁 Requesting access token...\n")
token_url = "https://api.fitbit.com/oauth2/token"
data = {
    "client_id": CLIENT_ID,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI,
    "code": code
}

response = requests.post(
    token_url,
    data=data,
    auth=(CLIENT_ID, CLIENT_SECRET),
)

if response.status_code == 200:
    print("✅ Access Token Info:\n")
    print(response.json())
    with open("fitbit_token.json", "w") as f:
        import json
        json.dump(response.json(), f, indent=2)
    print("\n💾 Token saved as fitbit_token.json — upload it to:")
    print("/home/rafa1215/consensus-project/secrets/")
else:
    print(f"❌ Token request failed ({response.status_code})")
    print(response.text)
