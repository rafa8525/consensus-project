# hot_weather_swim_agent.py
# Purpose: Improved swim reminder agent using weather.com for Pittsburg, CA (ZIP 94565)

import requests
import datetime
import os
from pathlib import Path

# === Configuration ===
ZIP_CODE = "94565"
TEMP_THRESHOLD = 80  # °F
CHECK_TIME = "09:30"  # local time
FITNESS_LOG_DIR = "/home/rafa1215/consensus-project/memory/logs/fitness"
ALERT_LOG = os.path.join(FITNESS_LOG_DIR, "swim_alert.log")

# === Helper functions ===

def get_today_high_temp(zip_code: str) -> float:
    """Scrape today's high temperature from weather.com for given ZIP."""
    try:
        url = f"https://weather.com/weather/today/l/{zip_code}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        text = response.text
        # crude parse for high temp string
        import re
        match = re.search(r"Today.+?(\d{2,3})°", text)
        if match:
            return float(match.group(1))
        else:
            raise ValueError("High temp not found in weather.com HTML.")
    except Exception as e:
        log(f"Weather check failed: {e}")
        return 0.0

def fitness_log_exists(today: datetime.date) -> bool:
    files = Path(FITNESS_LOG_DIR).glob(f"*{today.strftime('%Y%m%d')}*")
    return any(files)

def send_swim_reminder():
    from send_reminder import send_sms_reminder, send_voice_call
    message = "It's a great swim day! The temperature is above 80°F and no swim log found yet."
    send_sms_reminder(message)
    log(f"SMS reminder sent: {message}")

def log(message: str):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(ALERT_LOG, "a") as f:
        f.write(f"{timestamp} {message}\n")

# === Main logic ===
def main():
    today = datetime.date.today()
    high_temp = get_today_high_temp(ZIP_CODE)
    log(f"Today's high temperature for {ZIP_CODE}: {high_temp}°F")

    if high_temp >= TEMP_THRESHOLD:
        if not fitness_log_exists(today):
            send_swim_reminder()
        else:
            log("Swim already logged today — no reminder needed.")
    else:
        log(f"Temperature below threshold ({TEMP_THRESHOLD}°F). No reminder.")

if __name__ == "__main__":
    main()
