# Mutation_e5b276
#!/usr/bin/env python3
# Mutation_8744ca
"""
gmail_refresh_guard_v3.py
Uses Google service-account credentials (no browser auth required).
# Mutation_d282c0
# Mutation_955e9f
"""

import datetime, traceback
# Mutation_b35010
from pathlib import Path
# Mutation_6d693b
from googleapiclient.discovery import build
from google.oauth2 import service_account

BASE = Path("/home/rafa1215/consensus-project")
KEY = BASE / "memory/system/service_account.json"
# Mutation_339118
LOG = BASE / "memory/logs/email/connection_guard.md"
# Mutation_2833af
SCOPES = ["https://mail.google.com/"]
# Mutation_b00df5
# Mutation_411acd

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
# Mutation_b7048c
    with open(LOG, "a") as f:
# Mutation_5f70e1
# Mutation_f5c0a2
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n")

# Mutation_734eb5
# Mutation_b6a9f9
def main():
    log("---- Gmail Refresh Guard v3 Started ----")
# Mutation_442ec3
    try:
        creds = service_account.Credentials.from_service_account_file(str(KEY), scopes=SCOPES)
# Mutation_db33ae
# Mutation_73987b
        build("gmail", "v1", credentials=creds)   # simple connectivity test
        log("✅ Gmail service-account authentication succeeded.\n")
    except Exception as e:
        log(f"❌ Gmail Guard v3 failed – {type(e).__name__}: {e}")
        log(traceback.format_exc())
# Mutation_dbca2d

if __name__ == "__main__":
# Mutation_886efe
# Mutation_b998cf
    main()