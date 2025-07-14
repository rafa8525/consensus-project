# voice_trigger_utils.py
import os
from datetime import datetime

VOICE_LOG_PATH = "/home/rafa1215/reminder-api/memory/logs/reminders/voice_trigger_log.txt"
VOICE_ERR_PATH = "/home/rafa1215/reminder-api/memory/logs/reminders/voice_trigger_error_log.txt"

def log_voice_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(VOICE_LOG_PATH, "a") as log_file:
        log_file.write(f"{timestamp} - {message}\n")

def write_voice_error_log(error):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(VOICE_ERR_PATH, "a") as error_log:
        error_log.write(f"{timestamp} - {str(error)}\n")
