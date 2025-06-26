
import os
import shutil
import subprocess

# Define paths and filenames
local_file_path = "active_tasks_checklist.md"
target_repo_path = "memory/active_tasks_checklist.md"
commit_message = "✅ Add active_tasks_checklist.md – auto-generated on 2025-06-26"

# Ensure 'memory' directory exists
os.makedirs("memory", exist_ok=True)

# Copy checklist file to the memory directory
if not os.path.exists(local_file_path):
    raise FileNotFoundError(f"Required file not found: {local_file_path}")

shutil.copy(local_file_path, target_repo_path)

# Git add, commit, push
subprocess.run(["git", "add", target_repo_path], check=True)
subprocess.run(["git", "commit", "-m", commit_message], check=True)
subprocess.run(["git", "push"], check=True)

print("✅ active_tasks_checklist.md successfully pushed to GitHub.")
