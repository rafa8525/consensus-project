# swim_weather_nudge.py
import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# 👇 Add the full path to reminder-api to enable import
sys.path.append('/home/rafa1215/reminder-api')

# 👇 Now import send_sms
from send_reminder import send_sms

# 👇 Load .env from root
load_dotenv(dotenv_path='/home/rafa1215/.env')

def fetch_weather(api_key, zipcode):
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={zipcode}&aqi=no"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        temp_f = data['current']['temp_f']
        return temp_f
    except Exception as e:
        print(f"[{datetime.now()}] Weather fetch failed: {e}")
        if os.getenv("SMS_ENABLED", "false").lower() == "true":
            send_sms("⚠️ Weather fetch failed — check swim reminder manually.")
        return None

def main():
    weather_api_key = os.getenv("WEATHER_API_KEY")
    zipcode = "94565"

    if not weather_api_key:
        print(f"[{datetime.now()}] WEATHER_API_KEY missing in .env")
        return

    temp = fetch_weather(weather_api_key, zipcode)
    if temp is None:
        return

    print(f"[{datetime.now()}] Current temp in {zipcode}: {temp}°F")

    if temp > 80:
        message = f"☀️ It’s {temp}°F in Pittsburg. Perfect swim weather! Log your pool laps if you haven’t already."
        if os.getenv("SMS_ENABLED", "false").lower() == "true":
            send_sms(message)
        print(f"[{datetime.now()}] Reminder sent: {message}")
    else:
        print(f"[{datetime.now()}] Temp {temp}°F not high enough. No reminder sent.")

if __name__ == "__main__":
    main()
