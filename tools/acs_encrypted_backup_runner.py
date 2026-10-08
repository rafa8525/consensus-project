#!/usr/bin/env python3
"""Explicit ACS verified backup operation; not scheduled."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from tools import verified_backup_candidate as backup
from tools import secure_backup_transport_candidate as transport

SCOPE = "https://www.googleapis.com/auth/drive.file"

def drive_client(token):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(str(token), scopes=[SCOPE])
    if not creds.valid:
        creds.refresh(Request())
    return build("drive", "v3", credentials=creds, cache_discovery=False)

def execute(root, archive, encrypted, key, token, folder):
    if archive.exists() or encrypted.exists():
        raise FileExistsError("archive name already used")
    service = drive_client(token)
    backup.create(root, archive)
    transport.encrypt_file(archive, encrypted, key)
    verified = transport.verify_encrypted_archive(encrypted, key, backup)
    result = transport.upload_verified(encrypted, service, folder)
    recovered = transport.download_and_verify(
        result["remote_id"], service, verified["encrypted_sha256"], key, backup
    )
    if recovered["file_count"] != verified["file_count"]:
        raise ValueError("restored file count mismatch")
    return dict(status="uploaded_verified",
                finished_at_utc=datetime.now(timezone.utc).isoformat(),
                remote_id=result["remote_id"],
                encrypted_sha256=verified["encrypted_sha256"],
                file_count=recovered["file_count"],
                restore_verified=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", action="store_true")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--encrypted", type=Path, required=True)
    p.add_argument("--key", type=Path, required=True)
    p.add_argument("--token", type=Path, required=True)
    p.add_argument("--folder-id", required=True)
    args = p.parse_args()
    if not args.run:
        raise SystemExit("Explicit --run required")
    result = execute(args.root, args.archive, args.encrypted,
                     args.key, args.token, args.folder_id)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
