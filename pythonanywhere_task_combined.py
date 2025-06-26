#!/usr/bin/env python3
import subprocess
import datetime
import os

log_path = f"/home/rafa1215/consensus-project/logs/task_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
log = open(log_path, "w")

def run_command(command, label):
    log.write(f"\n=== {label} at {datetime.datetime.now()} ===\n")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        log.write(result.stdout)
        if result.stderr:
            log.write("\n[stderr]\n" + result.stderr)
        if result.returncode != 0:
            log.write(f"\n[Error] {label} failed with code {result.returncode}\n")
    except Exception as e:
        log.write(f"\n[Exception during {label}]: {str(e)}\n")

# Step 1: Git memory auto commit
run_command("python3 /home/rafa1215/consensus-project/memory_auto_commit_merged.py", "Memory Auto Commit")

# Step 2: Build daily digest
run_command("python3 /home/rafa1215/consensus-project/build_daily_digest.py", "Build Daily Digest")

# Step 3: Upload backup to Google Drive
run_command("python3 /home/rafa1215/consensus-project/backup_to_gdrive.py", "Google Drive Backup")

# Step 4: Barcode sheet updater
run_command("python3 /home/rafa1215/consensus-project/push_upc_corrections.py", "Barcode Sheet Auto-Update")

log.write(f"\n=== All tasks completed at {datetime.datetime.now()} ===\n")
log.close()
