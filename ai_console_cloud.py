from common.twilio_guard import send_sms
import os
import time
import requests
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime
import subprocess
from pathlib import Path

# Load .env
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

# Twilio credentials
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_PHONE = os.getenv("TWILIO_FROM_NUMBER")
TO_PHONE = os.getenv("TWILIO_TO_NUMBER")

# Corrected path
GIT_DIR = "/home/rafa1215/consensus-project"
LOG_DIR = os.path.join(GIT_DIR, "memory/logs")
last_error = ""

def send_sms(body):
    global last_error
    if body != last_error:
        try:
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            message = send_sms(
                body=body,
                from_=FROM_PHONE,
                to=TO_PHONE
            )
            print(f"✅ SMS sent: {body[:30]}... SID: {message.sid}")
            last_error = body
        except Exception as e:
            print(f"❌ SMS failed: {e}")
    else:
        print("⚠️ Repeated error detected — SMS not resent to avoid spam.")

def sync_logs():
    os.chdir(GIT_DIR)
    subprocess.run(["git", "pull"])
    subprocess.run(["git", "add", "."], check=True)
    commit_message = f"🔄 Auto-sync at {datetime.now().isoformat()}"
    subprocess.run(["git", "commit", "-m", commit_message])
    subprocess.run(["git", "push"])
    print("✅ GitHub sync complete.")

def run_cycle():
    print("🧠 AI Console Running — PythonAnywhere")
    send_sms("🤖 AI Console Cloud Agent is now active and syncing your system.")
    while True:
        try:
            sync_logs()
            time.sleep(3600)  # Run every hour
        except Exception as e:
            error_msg = f"⚠️ AI Console Error: {e}"
            print(error_msg)
            send_sms(error_msg)
            time.sleep(600)

if __name__ == "__main__":
    run_cycle()