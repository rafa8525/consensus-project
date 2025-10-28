#!/usr/bin/env python3
"""
cleanup_agent.py
Purpose: Automated cleanup utility for PythonAnywhere storage management.
Safely deletes or compresses redundant files to stay under the 5 GB quota.
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# === CONFIGURATION ===
HOME = Path.home()
ROOT = HOME / "consensus-project"
LOG_DIR = ROOT / "memory" / "logs" / "system"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "cleanup_agent.log"

# Directories to scan (extend as needed)
SCAN_PATHS = [
    HOME / "consensus-project",
    HOME / "tmp",
    HOME / ".cache",
]

# Skip important folders
EXCLUDE_DIRS = {
    "memory/logs/heartbeat",
    "memory/logs/system",
    "memory/logs/agents",
    ".git",
}

# Delete or compress criteria
MAX_FILE_AGE_DAYS = 30
MAX_FILE_SIZE_MB = 25

# === LOGGING ===
def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a") as f:
        f.write(f"[{timestamp}] {msg}\n")

# === UTILITIES ===
def is_excluded(path: Path) -> bool:
    for excl in EXCLUDE_DIRS:
        if excl in str(path):
            return True
    return False

def compress_file(path: Path):
    gz_path = path.with_suffix(path.suffix + ".gz")
    with open(path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    path.unlink()
    log(f"Compressed {path} → {gz_path}")

def should_delete(path: Path, now: datetime) -> bool:
    age_days = (now - datetime.fromtimestamp(path.stat().st_mtime)).days
    size_mb = path.stat().st_size / (1024 * 1024)
    return age_days > MAX_FILE_AGE_DAYS or size_mb > MAX_FILE_SIZE_MB

# === MAIN CLEANUP LOOP ===
def main():
    log("=== Cleanup Agent Started ===")
    now = datetime.now()
    files_deleted, files_compressed = 0, 0

    for scan_path in SCAN_PATHS:
        if not scan_path.exists():
            continue

        for path in scan_path.rglob("*"):
            if not path.is_file() or is_excluded(path):
                continue

            try:
                if should_delete(path, now):
                    if path.suffix in [".log", ".tmp", ".bak", ".tar", ".tar.gz"]:
                        path.unlink()
                        files_deleted += 1
                        log(f"Deleted {path}")
                    else:
                        compress_file(path)
                        files_compressed += 1
            except Exception as e:
                log(f"Error processing {path}: {e}")

    log(f"Completed. Deleted={files_deleted}, Compressed={files_compressed}")
    log("=== Cleanup Agent Finished ===\n")

# === ENTRY POINT ===
if __name__ == "__main__":
    main()
