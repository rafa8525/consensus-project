import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load .env tokens
load_dotenv(".env")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not GITHUB_TOKEN:
    print("❌ GITHUB_TOKEN not found in .env.")
    exit(1)

os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN
os.makedirs("logs", exist_ok=True)
log_path = "logs/daily_task.log"

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_path, "a") as f:
        f.write(f"{timestamp} {msg}\n")
    print(msg)

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log("⚠️ Telegram credentials not set. Skipping alert.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            log("📤 Telegram alert sent.")
        else:
            log(f"❌ Telegram alert failed: {response.status_code}")
    except Exception as e:
        log(f"❌ Telegram alert error: {e}")

log("🧠 Starting merged daily task...")

log("🚀 Running GitHub push for .md logs...")
result = subprocess.run(["python3", "push_existing_logs_only.py"], capture_output=True, text=True)
log(result.stdout.strip())
if result.stderr.strip():
    log(result.stderr.strip())

log("🗃️ Running ZIP archive upload...")
zip_result = subprocess.run(["python3", "zip_logs_and_push.py"], capture_output=True, text=True)
log(zip_result.stdout.strip())
if zip_result.stderr.strip():
    log(zip_result.stderr.strip())

# --- New: Run Reminder Agent ---
log("⏰ Running reminder agent...")
reminder_result = subprocess.run([
    "python3.10",
    "/home/rafa1215/consensus-project/reminder agent/reminder_agent.py"
], capture_output=True, text=True)
log(reminder_result.stdout.strip())
if reminder_result.stderr.strip():
    log(reminder_result.stderr.strip())

log("✅ Daily task completed.")
send_telegram_alert("✅ GitHub log sync + ZIP archive + reminders complete.")
