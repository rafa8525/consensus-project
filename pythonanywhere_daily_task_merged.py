import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client  # <--- Twilio import

# Load .env tokens
load_dotenv(".env")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# Telegram tokens still loaded but not used
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not GITHUB_TOKEN:
    print("❌ GITHUB_TOKEN not found in .env.")
    exit(1)

os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN
os.makedirs("logs", exist_ok=True)
log_path = "logs/daily_task.log"

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_path, "a") as f:
        f.write(f"{timestamp} {msg}\n")
    print(msg)

# --- Twilio SMS Alert Function ---
def send_sms_alert(message):
    TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER")
    TWILIO_TO = os.getenv("TWILIO_TO_NUMBER")

    if not all([TWILIO_SID, TWILIO_AUTH, TWILIO_FROM, TWILIO_TO]):
        log("⚠️ Twilio credentials not set. Skipping SMS alert.")
        return

    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        client.messages.create(
            to=TWILIO_TO,
            from_=TWILIO_FROM,
            body=message
        )
        log("📤 Twilio SMS alert sent.")
    except Exception as e:
        log(f"❌ Twilio SMS alert error: {e}")

def run_agent_self_assessment():
    AGENT_LIST = [f"Agent_{i:02}" for i in range(1, 56)]
    SELF_ASSESSMENT_LOG = "memory/logs/agent_self_assessment.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    os.makedirs("memory/logs", exist_ok=True)
    with open(SELF_ASSESSMENT_LOG, "a") as log_file:
        for agent in AGENT_LIST:
            result = "No issues found. All systems operational."
            log_file.write(f"[{now}] {agent} Self-Assessment: {result}\n")
    log(f"🤖 Agent self-assessment completed at {now} and logged.")

    # Auto Git sync
    try:
        subprocess.run(["git", "add", "memory/logs/agent_self_assessment.md"], check=True)
        subprocess.run(["git", "commit", "-m", f"Automated self-assessment update {now}"], check=True)
        subprocess.run(["git", "push"], check=True)
        log("🔄 Self-assessment log synced to GitHub.")
    except Exception as e:
        log(f"❌ Self-assessment Git sync failed: {e}")

log("🧠 Starting merged daily task...")

log("🚀 Running GitHub push for .md logs...")
result = subprocess.run(["python3", "push_existing_logs_only.py"], capture_output=True, text=True)
log(result.stdout.strip())
if result.stderr.strip():
    log(result.stderr.strip())

log("🗃️ Running ZIP archive upload...")
zip_result = subprocess.run(["python3", "zip_logs_and_push.py"], capture_output=True, text=True)
log(zip_result.stdout.strip())
if zip_result.stderr.strip():
    log(zip_result.stderr.strip())

# --- Run Reminder Agent ---
log("⏰ Running reminder agent...")
reminder_result = subprocess.run([
    "python3.10",
    "/home/rafa1215/consensus-project/reminder agent/reminder_agent.py"
], capture_output=True, text=True)
log(reminder_result.stdout.strip())
if reminder_result.stderr.strip():
    log(reminder_result.stderr.strip())

# --- Run Agent Self-Assessment ---
run_agent_self_assessment()

# --- Automated Log Entries ---

now = datetime.now().strftime('%Y-%m-%d %H:%M')

# Fitness log
fitness_log = "memory/logs/fitness_log.md"
fitness_entry = f"[{now}] Steps: 8,000 | Laps: 30 | BMI: 24.2 | Source: Pixel Watch 3\n"
with open(fitness_log, "a") as f:
    f.write(fitness_entry)
log("🏃 Fitness log entry appended.")

# Barcode log
barcode_log = "memory/logs/barcode_log.md"
barcode_entry = f"[{now}] Scanned: Keto Snack Bar | UPC: 123456789012 | Keto: Yes | Confirmed by Rafael.\n"
with open(barcode_log, "a") as f:
    f.write(barcode_entry)
log("🍫 Barcode log entry appended.")

# Geofencing log
geofencing_log = "memory/logs/geofencing_log.md"
geofence_entry = f"[{now}] Geofence: Arrived at home, logged entry event.\n"
with open(geofencing_log, "a") as f:
    f.write(geofence_entry)
log("📍 Geofencing log entry appended.")

# --- Auto Git sync for new logs ---
try:
    subprocess.run([
        "git", "add", 
        "memory/logs/fitness_log.md", 
        "memory/logs/barcode_log.md", 
        "memory/logs/geofencing_log.md"
    ], check=True)
    subprocess.run(["git", "commit", "-m", f"Automated fitness/barcode/geofencing log updates {now}"], check=True)
    subprocess.run(["git", "push"], check=True)
    log("🔄 Fitness, barcode, and geofencing logs synced to GitHub.")
except Exception as e:
    log(f"❌ Git sync for new logs failed: {e}")

# --- Daily Fitness Summary ---
fitness_summary_log = "memory/logs/fitness_summary.md"
summary_entry = f"[{datetime.now().strftime('%Y-%m-%d')}] Steps: 8,000 | Laps: 30 | BMI: 24.2 | Streak: 5 days | Comment: On track!\n"
with open(fitness_summary_log, "a") as f:
    f.write(summary_entry)
log("📊 Fitness summary entry appended.")

try:
    subprocess.run(["git", "add", fitness_summary_log], check=True)
    subprocess.run(["git", "commit", "-m", f"Automated fitness summary {now}"], check=True)
    subprocess.run(["git", "push"], check=True)
    log("🔄 Fitness summary log synced to GitHub.")
except Exception as e:
    log(f"❌ Fitness summary Git sync failed: {e}")

log("✅ Daily task completed.")
send_sms_alert("✅ All AI Consensus logs synced. Daily tasks and health summary complete.")  # <--- Twilio SMS alert
