#!/usr/bin/env python3
"""Fetch Health Connect export from a user-authorized Drive folder to PRIVATE cloud storage.

Designed for a PythonAnywhere scheduled task; never writes inside the Git
worktree. Uses an existing PRIVATE Google OAuth token with Drive read scope.
No browser/local-PC dependency during normal runs.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import tempfile

MAX_ZIP_BYTES = 800 * 1024 * 1024
DRIVE_API = "https://www.googleapis.com/drive/v3/files"

class DownloadError(Exception):
    pass

def download(folder_id: str, token_file: Path, target_dir: Path) -> Path:
    if not folder_id or any(c in folder_id for c in "'\\\n\r"):
        raise DownloadError("Missing or invalid Drive folder ID")
    if not token_file.is_file() or token_file.is_symlink():
        raise DownloadError("Private Google OAuth token missing")
    if target_dir.is_symlink():
        raise DownloadError("Private target must not be a symlink")
    # Resolve and constrain output to the configured private runtime.
    private_root = Path(os.environ.get("ACS_PRIVATE_RUNTIME", str(Path.home() / "acs-runtime"))).resolve()
    destination = target_dir.resolve()
    if destination != private_root and private_root not in destination.parents:
        raise DownloadError("Destination must be within ACS_PRIVATE_RUNTIME")
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    import requests
    creds = Credentials.from_authorized_user_file(str(token_file))
    if not creds.valid:
        if not creds.refresh_token:
            raise DownloadError("Google authorization expired; interactive cloud-side reauthorization required")
        creds.refresh(Request())
    headers = {"Authorization": "Bearer " + creds.token}
    q = "'" + folder_id + "' in parents and name = 'Health Connect.zip' and trashed = false"
    with requests.Session() as session:
        listing = session.get(DRIVE_API, headers=headers, params={
            "q": q, "fields": "nextPageToken,files(id,name,mimeType,size,modifiedTime,parents)",
            "page_size": 100, "pageSize": 100, "orderBy": "modifiedTime desc"
        }, timeout=35)
        listing.raise_for_status()
        payload = listing.json()
        items = payload.get("files") or []
        if not items:
            raise DownloadError("No Health Connect.zip accessible in the configured Drive folder")
        if payload.get("nextPageToken"):
            raise DownloadError("Too many matching exports; refusing ambiguous selection")
        latest = items[0]
        if latest.get("name") != "Health Connect.zip" or folder_id not in latest.get("parents", []):
            raise DownloadError("Unexpected Drive file identity")
        if latest.get("mimeType") != "application/zip":
            raise DownloadError("Drive item is not a ZIP file")
        nbytes = int(latest.get("size", "0"))
        if nbytes <= 0 or nbytes > MAX_ZIP_BYTES:
            raise DownloadError("Export size invalid")
        changed = datetime.fromisoformat(latest["modifiedTime"].replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - changed).total_seconds()
        if not 0 <= age <= 48 * 3600:
            raise DownloadError("Drive export missing freshness requirement (48 hours)")
        destination.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(destination, 0o700)
        tempname = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination, prefix=".health-connect-", suffix=".part", delete=False) as handle:
                tempname = Path(handle.name)
                os.chmod(tempname, 0o600)
                received = 0
                with session.get(DRIVE_API + "/" + latest["id"], params={"alt": "media"},
                                 headers=headers, stream=True, timeout=(15, 120)) as response:
                    response.raise_for_status()
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            received += len(chunk)
                            if received > MAX_ZIP_BYTES:
                                raise DownloadError("Download exceeded size limit")
                            handle.write(chunk)
                if received != nbytes:
                    raise DownloadError("Incomplete export download")
            output = destination / "Health Connect.zip"
            os.replace(tempname, output)
            return output
        finally:
            if tempname is not None:
                tempname.unlink(missing_ok=True)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder-id", default=os.environ.get("ACS_HC_DRIVE_FOLDER_ID", ""))
    parser.add_argument("--token", type=Path, default=Path.home() / ".secrets/google/token_gmail.json")
    parser.add_argument("--output-dir", type=Path, default=Path.home() / "acs-runtime/health-connect")
    args = parser.parse_args()
    try:
        file = download(args.folder_id, args.token, args.output_dir)
        print("ACS03_CLOUD_DOWNLOAD=PASS")
        print("PRIVATE_EXPORT_READY=YES")
        return 0
    except Exception as exc:
        # Redact credentials and exception strings; log only the type.
        print("ACS03_CLOUD_DOWNLOAD=FAIL " + type(exc).__name__, file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
