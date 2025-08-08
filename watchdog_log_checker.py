
import os
import json
import datetime
from twilio.rest import Client
import logging

# === Configuration ===
LOG_FILES = {
    "heartbeat_log.txt": "memory/logs/system/heartbeat_log.txt",
    "sms_simulation_log.txt": "memory/logs/system/sms_simulation_log.txt",
    "wsgi_restart_log.txt": "memory/logs/system/wsgi_restart_log.txt"
}
ALERT_STATE_FILE = "memory/logs/watchdog/alert_state.json"
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_TO = os.getenv("TWILIO_TO_NUMBER")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
logging.basicConfig(filename="memory/logs/watchdog/failure_log.txt", level=logging.INFO, format='[%(asctime)s] %(message)s')

# === Helper Functions ===
def has_alert_been_sent_today():
    if not os.path.exists(ALERT_STATE_FILE):
        return False
    try:
        with open(ALERT_STATE_FILE, 'r') as f:
            state = json.load(f)
        return state.get("last_alert_date") == str(datetime.date.today())
    except Exception as e:
        logging.error(f"Failed to read alert state file: {e}")
        return False

def mark_alert_sent_today():
    try:
        os.makedirs(os.path.dirname(ALERT_STATE_FILE), exist_ok=True)
        with open(ALERT_STATE_FILE, 'w') as f:
            json.dump({"last_alert_date": str(datetime.date.today())}, f)
    except Exception as e:
        logging.error(f"Failed to write alert state file: {e}")

def send_sms_alert(message):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        logging.info("[SMS SENT] " + message.replace("\n", " | "))
    except Exception as e:
        logging.error("[SMS FAILED] " + str(e))

def run_watchdog_check():
    if has_alert_been_sent_today():
        logging.info("Alert already sent today. Skipping SMS.")
        return

    missing = []
    for label, path in LOG_FILES.items():
        if not os.path.exists(path):
            missing.append(f"❌ {label} missing.")

    if missing:
        alert = "Watchdog Alert:\n" + "\n".join(missing)
        print("[INFO] Sending SMS alert:\n" + alert)
        send_sms_alert(alert)
        mark_alert_sent_today()
    else:
        logging.info("All log files present. No alert sent.")

if __name__ == "__main__":
    run_watchdog_check()
