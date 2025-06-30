
import os
import subprocess

logs_to_push = [
    ("upload_sync/manual_push/kitchen_log.md", "memory/logs/geofencing/kitchen_log.md"),
    ("upload_sync/manual_push/meal_log.md", "memory/logs/nutrition/meal_log.md"),
    ("upload_sync/manual_push/heart_log.md", "memory/logs/fitness/heart_log.md"),
    ("upload_sync/manual_push/transit_log.md", "memory/logs/transport/transit_log.md"),
]

print("📤 Smart uploader started...")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("❌ GITHUB_TOKEN environment variable not set.")
    exit(1)

env = os.environ.copy()
env["GITHUB_TOKEN"] = GITHUB_TOKEN

for local_path, remote_path in logs_to_push:
    if os.path.exists(local_path):
        print(f"✅ Found {local_path}, uploading...")
        subprocess.run(["python3", "batch_push_md.py", local_path, remote_path], env=env)
    else:
        print(f"❌ {local_path} not found. Skipping.")

print("✅ Done.")
