# agents/send_digest.py

import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email_digest():
    digest_path = os.path.join("logs", "daily_digest.txt")
    if not os.path.exists(digest_path):
        print("❌ Digest not found.")
        return

    with open(digest_path, "r", encoding="utf-8") as f:
        content = f.read()

    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(content)
    msg['Subject'] = '🧠 AI Consensus - Daily Digest'
    msg['From'] = email_address
    msg['To'] = email_address

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_address, email_password)
            smtp.send_message(msg)
        print("✅ Digest sent to your inbox.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    send_email_digest()
