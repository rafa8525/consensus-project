import os
import time
from datetime import datetime, timedelta
from twilio.rest import Client
from dotenv import load_dotenv
import subprocess
import logging

# Load environment variables
load_dotenv()

# Twilio config from .env
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_TO_NUMBER = os.getenv("TWILIO_TO_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Files and their max allowed stale duration (in seconds)
MONITORED_LOGS = {
    "/home/rafa1215/consensus-project/memory/logs/watchdog/heartbeat_log.txt": 6 * 3600,
    "/home/rafa1215/consensus-project/memory/logs/watchdog/sms_simulation_log.txt": 6 * 3600,
    "/home/rafa1215/consensus-project/memory/logs/watchdog/wsgi_restart_log.txt": 24 * 3600,
}

# Mapping of log files to recovery shell commands (customize as needed)
RECOVERY_COMMANDS = {
    "heartbeat_log.txt": "pkill -f heartbeat_logger.py && nohup python3 /home/rafa1215/consensus-project/heartbeat_logger.py &",
    "sms_simulation_log.txt": "pkill -f simulate_sms_test.py && nohup python3 /home/rafa1215/consensus-project/simulate_sms_test.py &",
    "wsgi_restart_log.txt": "sudo systemctl restart your_wsgi_service_name",  # Replace with actual WSGI restart command
}

LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/watchdog/health_monitor.log"

logging.basicConfig(filename=LOG_FILE,
                    level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def send_sms_alert(message):
    client.messages.create(
        body=message,
        from_=TWILIO_FROM_NUMBER,
        to=TWILIO_TO_NUMBER
    )
    logging.info(f"SMS alert sent: {message}")

def check_and_recover():
    now = time.time()
    alerts = []
    for filepath, max_age_sec in MONITORED_LOGS.items():
        if not os.path.exists(filepath):
            alerts.append(f"❌ {os.path.basename(filepath)} missing!")
            logging.error(f"Missing log file: {filepath}")
            continue
        last_modified = os.path.getmtime(filepath)
        age = now - last_modified
        if age > max_age_sec:
            alerts.append(f"❌ {os.path.basename(filepath)} not updated in last {age//3600:.0f} hours.")
            logging.warning(f"{filepath} last modified {age} seconds ago - stale.")
            # Try recovery
            cmd = RECOVERY_COMMANDS.get(os.path.basename(filepath))
            if cmd:
                try:
                    subprocess.Popen(cmd, shell=True)
                    logging.info(f"Recovery command executed for {filepath}: {cmd}")
                except Exception as e:
                    logging.error(f"Failed to execute recovery command for {filepath}: {e}")
            else:
                logging.warning(f"No recovery command defined for {filepath}")
        else:
            logging.info(f"{filepath} is fresh. Last modified {age} seconds ago.")

    if alerts:
        alert_message = "Watchdog Alert:\n" + "\n".join(alerts)
        send_sms_alert(alert_message)

def main():
    while True:
        try:
            check_and_recover()
        except Exception as e:
            logging.error(f"Health monitor failed: {e}")
        time.sleep(300)  # 5 minutes interval

if __name__ == "__main__":
    main()
