import os
import shutil
from datetime import datetime

# Base directory for logs
BASE_DIR = os.path.expanduser("~/consensus-project/memory/logs/system")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Files to rotate: { filename: prefix }
LOG_FILES = {
    "mcl_guard_heartbeat.log": "mcl_guard_heartbeat",
    "heartbeat.log": "heartbeat",
    "digest_cron.log": "digest_cron",
    "cleanup_agent.log": "cleanup_agent",
    "sync_visibility.log": "sync_visibility",
    "feedback_loop.log": "feedback_loop",
    "heartbeat_master.log": "heartbeat_master",
    "watchdog_alerts.log": "watchdog_alerts",
    "storage_cleanup.log": "storage_cleanup",
    "cron_diag.log": "cron_diag",
    "evolution_cycles.log": "evolution_cycles",
    "absorb_guard.log": "absorb_guard",
    "voice_worker.log": "voice_worker",
    "voice_trigger_heartbeat.log": "voice_trigger_heartbeat"  # ✅ NEW
}

def rotate_log_file(file_name, prefix):
    source_path = os.path.join(BASE_DIR, file_name)
    if os.path.exists(source_path) and os.path.getsize(source_path) > 0:
        timestamp = datetime.now().isoformat(timespec='seconds').replace(":", "-")
        dest_file = f"{prefix}_{timestamp}.log"
        dest_path = os.path.join(ARCHIVE_DIR, dest_file)
        shutil.move(source_path, dest_path)
        print(f"✅ Rotated: {file_name} → {dest_file}")
    else:
        print(f"⏭️ Skipped: {file_name} (not found or empty)")

def main():
    for filename, prefix in LOG_FILES.items():
        rotate_log_file(filename, prefix)

if __name__ == "__main__":
    main()
