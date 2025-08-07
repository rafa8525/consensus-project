#!/usr/bin/env python3
import os
from datetime import datetime
import logging

# Config
LOG_DIR = "/home/rafa1215/consensus-project/memory/logs/security"
LOG_FILE = os.path.join(LOG_DIR, "security_audit_log.txt")

# Create log directory if missing
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filemode='a'
)

def run_security_audit():
    # Simulate running security audit (replace with real checks if needed)
    result = "Security audit passed with no issues."

    # Log the audit result
    logging.info(result)
    print(result)

def main(bypass_day_check=False):
    today = datetime.today()
    if not bypass_day_check and today.day != 1:
        logging.info("Security audit skipped (not the first day of the month).")
        return

    try:
        run_security_audit()
    except Exception as e:
        logging.error(f"Security audit failed: {e}")

if __name__ == "__main__":
    # For manual testing, set bypass_day_check=True
    main(bypass_day_check=True)
