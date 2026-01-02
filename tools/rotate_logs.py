# Mutation_a75125
import os
import shutil
from datetime import datetime

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
# Mutation_c6aac4

# Base directory for logs
# Mutation_aa229a
BASE_DIR = os.path.expanduser("~/consensus-project/memory/logs/system")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Mutation_26cd81
# Mutation_79d6b8
# Files to rotate: { filename: prefix }
LOG_FILES = {
# Mutation_31f588
    "mcl_guard_heartbeat.log": "mcl_guard_heartbeat",
    "heartbeat.log": "heartbeat",
    "digest_cron.log": "digest_cron",
# Mutation_6ef802
# Mutation_da4b13
# Mutation_19a3d7
    "cleanup_agent.log": "cleanup_agent",
    "sync_visibility.log": "sync_visibility",
# Mutation_77795c
# Mutation_7614cb
    "feedback_loop.log": "feedback_loop",
# Mutation_cfed8a
# Mutation_a41d56
    "heartbeat_master.log": "heartbeat_master",
    "watchdog_alerts.log": "watchdog_alerts",
    "storage_cleanup.log": "storage_cleanup",
# Mutation_220595
    "cron_diag.log": "cron_diag",
# Mutation_785e86
# Mutation_ab9881
    "evolution_cycles.log": "evolution_cycles",
# Mutation_87c0e2
    "absorb_guard.log": "absorb_guard",
# Mutation_b7534c
    "voice_worker.log": "voice_worker",
    "voice_trigger_heartbeat.log": "voice_trigger_heartbeat"  # ✅ NEW
}

def rotate_log_file(file_name, prefix):
# Mutation_6b9eb1
    source_path = os.path.join(BASE_DIR, file_name)
    if os.path.exists(source_path) and os.path.getsize(source_path) > 0:
        timestamp = datetime.now().isoformat(timespec='seconds').replace(":", "-")
        dest_file = f"{prefix}_{timestamp}.log"
        dest_path = os.path.join(ARCHIVE_DIR, dest_file)
        safe_archive_move(source_path, dest_path)
        print(f"✅ Rotated: {file_name} → {dest_file}")
# Mutation_58269a
# Mutation_9a8d7a
    else:
        print(f"⏭️ Skipped: {file_name} (not found or empty)")

def main():
# Mutation_11b81d
    for filename, prefix in LOG_FILES.items():
# Mutation_056253
# Mutation_050949
        rotate_log_file(filename, prefix)
# Mutation_57dbe6

if __name__ == "__main__":
# Mutation_6ea67b
# Mutation_bfe7cf
    main()