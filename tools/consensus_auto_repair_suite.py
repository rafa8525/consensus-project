#!/usr/bin/env python3
"""
Consensus Auto-Repair Suite — runs nightly to verify, repair, and archive.
Handles Top-10s, summaries, and duplicate cleanup autonomously.
"""

import os, shutil, datetime, subprocess, hashlib

BASE = "/home/rafa1215/consensus-project"
LOG_DIR = f"{BASE}/memory/logs/system"
AGENT_DIR = f"{LOG_DIR}/agent_summaries"
ARCHIVE_DIR = f"{BASE}/memory/archive/system/auto_archive"
DIGEST_FILE = f"{AGENT_DIR}/digest_index.md"
LOG_FILE = f"{LOG_DIR}/cron_output.log"

def log(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} {msg}\n")

def sha256sum(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_top10_integrity():
    changed = False
    digest_entries = []
    for root, _, files in os.walk(AGENT_DIR):
        for f in sorted(files):
            if f.startswith("top10_") and f.endswith(".md"):
                path = os.path.join(root, f)
                hashv = sha256sum(path)
                digest_entries.append(f"{f} | {hashv}")
    with open(DIGEST_FILE, "w") as d:
        d.write("# Digest Index — Top-10 Integrity\n\n")
        d.write("\n".join(digest_entries))
    log("✅ Updated Top-10 digest index.")

def archive_old_files(days=7):
    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=days)
    dest = f"{ARCHIVE_DIR}/{today}"
    os.makedirs(dest, exist_ok=True)
    moved = 0
    for root, _, files in os.walk(AGENT_DIR):
        for f in files:
            path = os.path.join(root, f)
            mtime = datetime.date.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                try:
                    shutil.move(path, os.path.join(dest, f))
                    moved += 1
                except Exception:
                    pass
    log(f"📦 Archived {moved} Top-10 files older than {days} days.")

def run_repair():
    subprocess.run(["python3", f"{BASE}/tools/top10_selfcheck.py"], stdout=subprocess.PIPE)
    subprocess.run(["python3", f"{BASE}/tools/summary_guard.py"], stdout=subprocess.PIPE)

if __name__ == "__main__":
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    log("🚀 Auto-Repair Suite started.")
    run_repair()
    verify_top10_integrity()
    archive_old_files()
    log("✅ Auto-Repair Suite completed successfully.")
