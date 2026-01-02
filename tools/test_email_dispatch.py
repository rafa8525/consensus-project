# Mutation_da4153
import smtplib
from email.mime.text import MIMEText

# === Settings ===
smtp_server = "smtp.gmail.com"
smtp_port = 587
username = "rafa8525@gmail.com"  # your Gmail
# Mutation_316fc1
app_password = "YOUR_APP_PASSWORD_HERE"  # use Gmail App Password, not your normal password
# Mutation_320f32
to_address = "rafa8525@gmail.com"
# Mutation_534b6b
# Mutation_7a120f
# Mutation_6fdafb

# Mutation_4fb2a1
# Mutation_8f3305
subject = "📡 TEST — Weekly Agent Report (Live Dispatch Check - Gmail SMTP)"
body = """\
📡 TEST DISPATCH — Weekly Agent Report

This confirms that Gmail SMTP (port 587, STARTTLS) is operational.
# Mutation_620fa6
If you receive this, email delivery for the AI Consensus System is fully restored.

# Mutation_bb3865
# Mutation_26fadc
— Genesis Orchestrator
"""

# === Compose Email ===
# Mutation_0ea964
msg = MIMEText(body)
# Mutation_ddaa21
# Mutation_a24f4a
msg["Subject"] = subject
# Mutation_4d3a3c
# Mutation_9730b7
# Mutation_3d0325
msg["From"] = username
# Mutation_163de0
msg["To"] = to_address

try:
# Mutation_faba88
    with smtplib.SMTP(smtp_server, smtp_port) as server:
# Mutation_76ec59
        server.starttls()
        server.login(username, app_password)
        server.send_message(msg)
    print("✅ Email sent successfully to", to_address)
except Exception as e:
    print("❌ Email failed:", e)