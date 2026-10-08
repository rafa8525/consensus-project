#!/usr/bin/env python3
"""Run a harmless encrypted Google Drive probe using the existing service account.

Explicit --run flag required. Uploads only random synthetic bytes, verifies
remote metadata and downloaded ciphertext, then trashes ONLY its own remote
probe file. Does not read ACS memory or alter scheduled tasks.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from tools.secure_backup_transport_candidate import encrypt, decrypt, upload_verified

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DEFAULT_CREDENTIAL_FILE = Path.home() / ".secrets/google/service_account.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="required to perform a synthetic upload")
    parser.add_argument("--folder-id", required=True, help="existing Google Drive folder ID")
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CREDENTIAL_FILE)
    args = parser.parse_args()
    if not args.run:
        parser.error("explicit --run required; no changes made")
    if not args.credentials.is_file():
        raise SystemExit("FAIL: service account credentials not present")
    # Only synthetic data; ephemeral key is never transmitted or committed.
    key = os.urandom(32)
    original = os.urandom(4096)
    with tempfile.TemporaryDirectory(prefix="acs-probe-") as td:
        encrypted = Path(td) / ("acs-synthetic-probe-" + os.urandom(6).hex() + ".acsenc")
        encrypted.write_bytes(encrypt(original, key))
        encrypted.chmod(0o600)
        expected_sha = hashlib.sha256(encrypted.read_bytes()).hexdigest()
        creds = service_account.Credentials.from_service_account_file(
            str(args.credentials), scopes=SCOPES
        )
        drive = build("drive", "v3", credentials=creds, cache_discovery=False)
        remote_id = None
        try:
            receipt = upload_verified(encrypted, drive, args.folder_id)
            remote_id = receipt["remote_id"]
            output = io.BytesIO()
            downloader = MediaIoBaseDownload(output, drive.files().get_media(fileId=remote_id))
            done = False
            while not done:
                _, done = downloader.next_chunk()
                if output.tell() > 8192:
                    raise RuntimeError("unexpectedly large probe download")
            blob = output.getvalue()
            if hashlib.sha256(blob).hexdigest() != expected_sha:
                raise RuntimeError("remote SHA-256 mismatch")
            if decrypt(blob, key) != original:
                raise RuntimeError("remote decrypted data mismatch")
            print(json.dumps({"result": "PASS", "synthetic": True,
                              "uploaded_bytes": len(blob),
                              "encrypted_download_and_decryption": "verified"}))
            return 0
        except Exception as exc:
            print(json.dumps({"result": "FAIL", "error_type": type(exc).__name__,
                              "reason": str(exc)[:250]}))
            return 1
        finally:
            if remote_id:
                try:
                    drive.files().update(fileId=remote_id, body={"trashed": True},
                                         fields="id,trashed").execute()
                    print("Synthetic remote probe moved to Drive Trash")
                except Exception:
                    print("WARNING: could not trash synthetic probe; remove it manually")


if __name__ == "__main__":
    raise SystemExit(main())
