import os
import re
import json
import datetime
import shutil
import hashlib

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

# ================================================================
#  AI Consensus System – Automated File Auditor and Cleaner
#  Author: Rafael Lymburner (2025-10-20)
#  Purpose: Detect unused, duplicate, or outdated files and
#            safely archive them with timestamped names.
# ================================================================

BASE = "/home/rafa1215/consensus-project"
TOOLS = f"{BASE}/tools"
ARCHIVE = f"{BASE}/memory/archive/auto_cleanup/{datetime.date.today()}"
LOG = f"{BASE}/memory/logs/system/cron_output.log"
HASH_DB = f"{BASE}/memory/logs/system/file_hash_history.json"

# ------------------------------------------------
# Utility: Logging helper
# ------------------------------------------------
def log(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG, "a") as f:
        f.write(f"{ts} {msg}\n")

# ------------------------------------------------
# Utility: Hash calculation for duplicate detection
# ------------------------------------------------
def hash_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

# ------------------------------------------------
# Load/save hash history to prevent re-archiving
# ------------------------------------------------
def load_hash_db():
    if os.path.exists(HASH_DB):
        with open(HASH_DB) as f:
            return json.load(f)
    return {}

def save_hash_db(db):
    with open(HASH_DB, "w") as f:
        json.dump(db, f, indent=2)

# ------------------------------------------------
# Discover active Python files still being used
# ------------------------------------------------
def get_active_references():
    active = set()
    for root, _, files in os.walk(TOOLS):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    with open(path) as src:
                        for line in src:
                            if re.search(r"(import |open\(|run\()", line):
                                active.update(re.findall(r"[\w_]+\.py", line))
                except Exception:
                    continue
    return active

# ------------------------------------------------
# Identify unused files older than 7 days
# ------------------------------------------------
def find_unused_files(active_refs):
    unused = []
    for root, _, files in os.walk(BASE):
        for f in files:
            if f.endswith((".py", ".log", ".json", ".csv", ".md")) and "archive" not in root:
                path = os.path.join(root, f)
                try:
                    if f not in active_refs:
                        age = (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(path))).days
                        if age >= 7:
                            unused.append(path)
                except Exception:
                    continue
    return unused

# ------------------------------------------------
# Archive with auto-rename if file already exists
# ------------------------------------------------
def archive_files(unused):
    os.makedirs(ARCHIVE, exist_ok=True)
    db = load_hash_db()
    archived_count = 0

    for f in unused:
        try:
            h = hash_file(f)
            if h not in db.values():  # skip identical files already archived
                filename = os.path.basename(f)
                dest = os.path.join(ARCHIVE, filename)

                # ✅ Auto-rename if duplicate name already exists
                if os.path.exists(dest):
                    base, ext = os.path.splitext(dest)
                    dest = f"{base}_{datetime.datetime.now().strftime('%H%M%S')}{ext}"

                safe_archive_move(f, dest)
                db[f] = h
                archived_count += 1
                log(f"📦 Archived unused file: {dest}")
            else:
                log(f"⏩ Skipped duplicate hash: {f}")
        except Exception as e:
            log(f"⚠️ Failed to archive {f}: {e}")

    save_hash_db(db)
    log(f"✅ Archived {archived_count} unused files to {ARCHIVE}")

# ------------------------------------------------
# Main execution
# ------------------------------------------------
if __name__ == "__main__":
    log("🔍 Running system file auditor...")
    active_refs = get_active_references()
    unused = find_unused_files(active_refs)
    if unused:
        archive_files(unused)
    else:
        log("✅ No new unused files detected. All clean.")
