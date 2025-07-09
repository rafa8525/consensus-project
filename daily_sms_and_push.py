import os
import datetime
import subprocess
from twilio.rest import Client

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# --- 1. Send SMS ---
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
target_number = os.getenv("TARGET_PHONE_NUMBER")

client = Client(account_sid, auth_token)

today = datetime.datetime.now().strftime("%Y-%m-%d")
message_body = f"📡 Morning status: All systems operational for {today}."

try:
    message = client.messages.create(
        body=message_body,
        from_=twilio_number,
        to=target_number
    )

    # --- 2. Log Message Locally ---
    log_dir = "memory/logs/twilio/"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"sms_log_{today}.md")

    with open(log_path, "w") as f:
        f.write(f"# SMS Log - {today}\n")
        f.write(f"- ✅ Message sent at {datetime.datetime.now().strftime('%H:%M:%S')}\n")
        f.write(f"- 📤 Content: {message_body}\n")
        f.write(f"- 🔁 SID: {message.sid}\n")

    print(f"✅ SMS sent and logged to {log_path}")

    # --- 3. GitHub Commit + Push ---
    subprocess.run(["git", "add", log_path], check=True)
    subprocess.run(["git", "commit", "-m", f"📨 Auto-log: SMS log for {today}"], check=True)
    subprocess.run(["git", "push", "origin", "v1.1-dev"], check=True)

    print("✅ Log committed and pushed to GitHub.")

except Exception as e:
    print(f"❌ Error: {e}")
