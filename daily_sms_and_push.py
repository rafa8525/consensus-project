#!/usr/bin/env python3
import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

LOG_FILE = '/home/rafa1215/consensus-project/memory/logs/agents/daily_sms_and_push.log'
os.makedirs(Path(LOG_FILE).parent, exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')

def load_env():
    env_path = Path("/home/rafa1215/consensus-project/.env")
    if env_path.exists():
        load_dotenv(env_path)
        logging.info("Loaded .env file.")
    else:
        logging.error(".env file not found.")
        raise FileNotFoundError(".env file not found.")

def validate_env_vars():
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_FROM_NUMBER', 'TWILIO_TO_NUMBER']
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        logging.error(f"Missing environment variables: {missing}")
        raise EnvironmentError(f"Missing environment variables: {missing}")
    logging.info("All required environment variables present.")

def send_sms(client, from_number, to_number, body):
    max_attempts = 3
    delay = 2
    for attempt in range(1, max_attempts + 1):
        try:
            logging.info(f"Attempt {attempt}: Sending SMS...")
            message = client.messages.create(
                body=body,
                from_=from_number,
                to=to_number
            )
            logging.info(f"SMS sent successfully, SID: {message.sid}")
            return True
        except TwilioRestException as e:
            logging.error(f"Twilio error on attempt {attempt}: {e}")
            if attempt < max_attempts:
                time.sleep(delay)
                delay *= 2
            else:
                raise

def main():
    try:
        load_env()
        validate_env_vars()
        client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        from_number = os.getenv('TWILIO_FROM_NUMBER')
        to_number = os.getenv('TWILIO_TO_NUMBER')
        body = "✅ Your daily SMS & push notifications are active."
        send_sms(client, from_number, to_number, body)
        logging.info("Daily SMS task completed successfully.")
    except Exception as e:
        logging.exception(f"Failed to send daily SMS: {e}")
        raise

if __name__ == "__main__":
    main()
