from common.twilio_guard import send_sms
import os
from pathlib import Path
from dotenv import load_dotenv
from twilio.rest import Client

# Show the current working directory and .env presence
print("🛠 Working directory:", Path().absolute())
print("📂 .env file exists here:", Path(".env").exists())

# Load environment variables from .env
load_dotenv()

# Retrieve credentials
account_sid = "AC4b4d18bdc5bc1b13f7bf2220a9d02287"
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# Debug output
print("🔑 AUTH TOKEN LOADED:", "Yes" if auth_token else "No (Check .env file)")
print("🧪 Loaded Token (raw):", repr(auth_token))

# Set numbers
twilio_number = "+18886607830"
target_number = "+16502283267"

# Initialize client and send message
client = Client(account_sid, auth_token)

message = send_sms(
    body="Hi Rafael, are you going on your 10:30 AM walk today?",
    from_=twilio_number,
    to=target_number
)

print("✅ Message sent. SID:", message.sid)
