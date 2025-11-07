import smtplib
from email.mime.text import MIMEText

# === Settings ===
smtp_server = "smtp.gmail.com"
smtp_port = 587
username = "rafa8525@gmail.com"  # your Gmail
app_password = "YOUR_APP_PASSWORD_HERE"  # use Gmail App Password, not your normal password
to_address = "rafa8525@gmail.com"

subject = "📡 TEST — Weekly Agent Report (Live Dispatch Check - Gmail SMTP)"
body = """\
📡 TEST DISPATCH — Weekly Agent Report

This confirms that Gmail SMTP (port 587, STARTTLS) is operational.
If you receive this, email delivery for the AI Consensus System is fully restored.

— Genesis Orchestrator
"""

# === Compose Email ===
msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = username
msg["To"] = to_address

try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, app_password)
        server.send_message(msg)
    print("✅ Email sent successfully to", to_address)
except Exception as e:
    print("❌ Email failed:", e)
