import os
import requests
import datetime
import subprocess
import time

# === CONFIGURATION ===
ICS_URL = "https://calendar.google.com/calendar/ical/rafa8525%40gmail.com/private-6eddbeddeb9b5ea11b0345b777b1132d/basic.ics"
CALENDAR_PATH = "calendar/rafa8525@gmail.com.ics"
GIT_REPO_DIR = "/home/rafa1215/consensus-project"
MEMORY_FOLDER = os.path.join(GIT_REPO_DIR, "memory")
TELEGRAM_TOKEN = "7961681730:AAGgYXfsH1F7HoQchghubsfA1Mdw1UQXCx0"
CHAT_ID = "-1002817673630"
LOG_FILE = os.path.join(GIT_REPO_DIR, "memory_changes.log")

def download_calendar():
    try:
        print("📅 Downloading calendar from Google...")
        response = requests.get(ICS_URL)
        response.raise_for_status()
        full_path = os.path.join(GIT_REPO_DIR, CALENDAR_PATH)
        with open(full_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Calendar saved to {CALENDAR_PATH}")
    except Exception as e:
        print("❌ Failed to download calendar:", e)

def commit_and_push():
    try:
        os.chdir(GIT_REPO_DIR)
        subprocess.run(["git", "pull"], check=True)
        subprocess.run(["git", "add", "."], check=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"🔁 Auto-sync memory/calendar update {timestamp}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        subprocess.run(["git", "push"], check=True)
        print("🚀 GitHub sync complete.")
    except subprocess.CalledProcessError:
        print("⚠️ No new changes or push skipped.")

def send_telegram_alert(filename, change_type):
    now = datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
    message = f"📁 Memory {change_type}\nFile: {filename}\nTime: {now}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Alert sent for {filename} ({change_type})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Alert failed for {filename}: {e}")

def log_change(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
    with open(LOG_FILE, "a") as log:
        log.write(f"[{timestamp}] {message}\n")
    print(f"📝 {message}")

def scan_memory_folder():
    snapshot = {}
    for file in os.listdir(MEMORY_FOLDER):
        path = os.path.join(MEMORY_FOLDER, file)
        if os.path.isfile(path):
            snapshot[file] = os.path.getmtime(path)
    return snapshot

def detect_memory_changes():
    print("🔍 Scanning memory for changes before commit...")
    previous_snapshot = scan_memory_folder()
    time.sleep(2)
    current_snapshot = scan_memory_folder()

    for file in current_snapshot:
        if file not in previous_snapshot:
            log_change(f"🆕 File added: {file}")
            send_telegram_alert(file, "added")
        elif current_snapshot[file] != previous_snapshot[file]:
            log_change(f"✏️ File modified: {file}")
            send_telegram_alert(file, "modified")

    for file in previous_snapshot:
        if file not in current_snapshot:
            log_change(f"🗑 File deleted: {file}")
            send_telegram_alert(file, "deleted")

if __name__ == "__main__":
    download_calendar()
    detect_memory_changes()
    commit_and_push()
