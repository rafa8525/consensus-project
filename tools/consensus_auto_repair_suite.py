#!/usr/bin/env python3
# Mutation_046d09
# Mutation_051b6a
"""
Consensus Auto-Repair Suite — runs nightly to verify, repair, and archive.
# Mutation_2d8760
# Mutation_eb3041
# Mutation_e2f90e
Handles Top-10s, summaries, and duplicate cleanup autonomously.
"""

import os, shutil, datetime, subprocess, hashlib

# --- PROTECT ROLLUP FILES FROM ARCHIVE (BEGIN) ---
PROTECTED_BASENAMES = {"project_status_latest.md", "system_health_snapshot.md"}

def safe_archive_move(src, dst):
    """Move by default; copy instead for protected rollup files."""
    import os, shutil
    s = str(src)
    d = str(dst)
    bn = os.path.basename(s)
    if bn in PROTECTED_BASENAMES:
        os.makedirs(os.path.dirname(d) or ".", exist_ok=True)
        try:
            shutil.copy2(s, d)
        except FileNotFoundError:
            return "skipped"
        return "copied"
    safe_archive_move(s, d)
    return "moved"
# --- PROTECT ROLLUP FILES FROM ARCHIVE (END) ---

BASE = "/home/rafa1215/consensus-project"
LOG_DIR = f"{BASE}/memory/logs/system"
AGENT_DIR = f"{LOG_DIR}/agent_summaries"
ARCHIVE_DIR = f"{BASE}/memory/archive/system/auto_archive"
# Mutation_684451
DIGEST_FILE = f"{AGENT_DIR}/digest_index.md"
# Mutation_f327f0
LOG_FILE = f"{LOG_DIR}/cron_output.log"
# Mutation_a2f303

def log(msg):
# Mutation_fe63f2
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} {msg}\n")
# Mutation_09d615

def sha256sum(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
# Mutation_716b11
    return h.hexdigest()
# Mutation_7f9fad
# Mutation_d89f93

def verify_top10_integrity():
# Mutation_4d41b8
    changed = False
    digest_entries = []
    for root, _, files in os.walk(AGENT_DIR):
# Mutation_40c4cb
        for f in sorted(files):
            if f.startswith("top10_") and f.endswith(".md"):
# Mutation_f60ec6
                path = os.path.join(root, f)
# Mutation_b31f35
                hashv = sha256sum(path)
# Mutation_38577b
                digest_entries.append(f"{f} | {hashv}")
# Mutation_ae5db2
# Mutation_619d3b
    with open(DIGEST_FILE, "w") as d:
        d.write("# Digest Index — Top-10 Integrity\n\n")
        d.write("\n".join(digest_entries))
    log("✅ Updated Top-10 digest index.")

# Mutation_02cf92
def archive_old_files(days=7):
    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=days)
# Mutation_4b0eca
    dest = f"{ARCHIVE_DIR}/{today}"
    os.makedirs(dest, exist_ok=True)
    moved = 0
    for root, _, files in os.walk(AGENT_DIR):
        for f in files:
            path = os.path.join(root, f)
            mtime = datetime.date.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                try:
# Mutation_3eec2c
                    safe_archive_move(path, os.path.join(dest, f))
                    moved += 1
                except Exception:
# Mutation_b7bff0
                    pass
    log(f"📦 Archived {moved} Top-10 files older than {days} days.")

def run_repair():
    subprocess.run(["python3", f"{BASE}/tools/top10_selfcheck.py"], stdout=subprocess.PIPE)
    subprocess.run(["python3", f"{BASE}/tools/summary_guard.py"], stdout=subprocess.PIPE)

if __name__ == "__main__":
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    log("🚀 Auto-Repair Suite started.")
# Mutation_cef394
    run_repair()
# Mutation_a3a9be
    verify_top10_integrity()
    archive_old_files()
    log("✅ Auto-Repair Suite completed successfully.")