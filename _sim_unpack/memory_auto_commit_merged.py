import os
import subprocess
import datetime

# === Step 1: Download Google Calendar ICS ===
print("📅 Downloading calendar from Google...")

calendar_url = "https://calendar.google.com/calendar/ical/rafa8525%40gmail.com/private-xxxx/basic.ics"
calendar_path = "calendar/rafa8525@gmail.com.ics"
os.makedirs("calendar", exist_ok=True)

try:
    import requests

    response = requests.get(calendar_url)
    response.raise_for_status()
    with open(calendar_path, "wb") as f:
        f.write(response.content)
    print(f"✅ Calendar saved to {calendar_path}")
except Exception as e:
    print(f"⚠️ Failed to download calendar: {e}")

# === Step 2: Git sync memory folder ===
print("🔍 Scanning memory for changes before commit...")

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
commit_message = f"🔁 Auto-sync memory/calendar update {timestamp}"

try:
    subprocess.run(["git", "pull"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "push"], check=True)
    print("🚀 GitHub sync complete.")
except subprocess.CalledProcessError as e:
    print(f"⚠️ No new changes or push skipped.\n{e}")

# === Step 3: Auto-generate daily digest after sync ===
print("📝 Generating daily digest...")

try:
    subprocess.run(
        ["python3", "/home/rafa1215/consensus-project/build_daily_digest.py"],
        check=True,
    )
    print(f"✅ Daily digest auto-generated at {datetime.datetime.now().isoformat()}")
except Exception as e:
    print(f"⚠️ Failed to generate daily digest: {e}")
