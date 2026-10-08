#!/usr/bin/env python3
"""Guarded entrypoint for one ACS backup cycle.

Not active unless invoked with --run. Writes a success record only after
remote download and manifest verification. Uses existing owner OAuth.
"""
from __future__ import annotations
import argparse
import fcntl
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from tools.acs_encrypted_backup_runner import execute

def record_success(path: Path, result: dict) -> None:
    fd, staging = tempfile.mkstemp(prefix=".acs-receipt-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(result, out, sort_keys=True)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(staging, path)
    finally:
        Path(staging).unlink(missing_ok=True)

def cycle(home: Path) -> dict:
    root = home / "consensus-project"
    secret_dir = home / ".secrets/google"
    local = home / "local_backups/acs"
    secret_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    local.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_file = secret_dir / "acs_backup.lock"
    fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        folder_file = secret_dir / "drive_backup_folder_id.txt"
        if folder_file.is_symlink():
            raise ValueError("invalid folder ID path")
        folder_id = folder_file.read_text().strip()
        if not folder_id or any(c.isspace() for c in folder_id):
            raise ValueError("invalid folder ID")
        moment = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        plain = local / ("acs_daily_" + moment + ".zip")
        cipher = local / ("acs_daily_" + moment + ".acsenc")
        result = execute(root, plain, cipher,
                         secret_dir / "acs_backup_aes256.key",
                         secret_dir / "drive_backup_token.json", folder_id)
        record_success(secret_dir / "acs_backup_success.json", result)
        plain.unlink()
        return {"status": "uploaded_verified", "file_count": result["file_count"],
                "restore_verified": True}
    finally:
        os.close(fd)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if not args.run:
        print(json.dumps({"status":"not_run","reason":"explicit --run required"}))
        return 2
    try:
        print(json.dumps(cycle(Path.home())))
        return 0
    except Exception as error:
        print(json.dumps({"status":"failed","error_type":type(error).__name__}))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
