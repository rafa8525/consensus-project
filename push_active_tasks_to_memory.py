
import os
import shutil
import subprocess

# Define file and commit message
file_to_commit = "memory/active_tasks_checklist.md"
local_file_path = "/mnt/data/active_tasks_checklist.md"
commit_message = "✅ Add active_tasks_checklist.md – auto-generated on 2025-06-26"

# Ensure memory directory exists
os.makedirs("memory", exist_ok=True)

# Copy file to memory/ directory
shutil.copy(local_file_path, file_to_commit)

# Run Git commands to commit and push
subprocess.run(["git", "add", file_to_commit])
subprocess.run(["git", "commit", "-m", commit_message])
subprocess.run(["git", "push"])
