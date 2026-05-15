#!/usr/bin/env python3
import subprocess
import time
import pytz
from datetime import datetime

# Timezone settings
TIMEZONE = pytz.timezone("America/Los_Angeles")
START_HOUR = 9   # 9 AM PDT
END_HOUR = 16    # 4 PM PDT

# Command to run your main scheduler
COMMAND = ["python3", "/home/rafa1215/memory/tools/reminder_scheduler.py"]

def within_allowed_window():
    now = datetime.now(TIMEZONE)
    return START_HOUR <= now.hour < END_HOUR

if __name__ == "__main__":
    while True:
        if within_allowed_window():
            subprocess.run(COMMAND)
        # Sleep until next hour
        time.sleep(3600)

