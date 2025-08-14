from common.twilio_guard import send_sms

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

# Setup logging
LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/agents/daily_sms_and_push.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def send_sms_via_twilio(body):
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_FROM_NUMBER")
        to_number = os.getenv("TWILIO_TO_NUMBER")
        if not all([account_sid, auth_token, from_number, to_number]):
            raise ValueError("Missing one or more Twilio environment variables.")
        client = Client(account_sid, auth_token)
        send_sms(body=body, from_=from_number, to=to_number)
        logging.info("SMS sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send SMS: {e}")

def write_status_log():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_log_path = "/home/rafa1215/consensus-project/memory/logs/system/heartbeat_schedule_status_{}.md".format(datetime.now().strftime("%Y-%m-%d"))
        with open(status_log_path, "a") as f:
            f.write(f"- ✅ {timestamp} - Daily push + GitHub sync completed.\n")
        logging.info("Status log updated.")
    except Exception as e:
        logging.error(f"Failed to update status log: {e}")

def sync_git_memory():
    try:
        os.system("cd /home/rafa1215/consensus-project && git add -A")
        commit_msg = f"Auto-log sync for {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        os.system(f"cd /home/rafa1215/consensus-project && git commit -m \"{commit_msg}\"")
        os.system("cd /home/rafa1215/consensus-project && git push origin v1.1-dev")
        logging.info("GitHub sync complete.")
    except Exception as e:
        logging.error(f"GitHub sync failed: {e}")

if __name__ == "__main__":
    try:
        logging.info("=== Daily SMS and Push Started ===")
        sync_git_memory()
        write_status_log()
        logging.info("=== Daily SMS and Push Completed ===")
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
