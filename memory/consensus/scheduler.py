# consensus/scheduler.py

import schedule
import time
from consensus import main
import agents.generate_digest as digest
import agents.send_digest as email_digest

def run_scheduled_task():
    print("🧠 Running main agent...")
    main.run()

    print("📅 Generating daily digest...")
    digest.generate_daily_digest()

    print("📤 Sending daily digest by email...")
    email_digest.send_email_digest()

def start_scheduler():
    schedule.every().day.at("10:00").do(run_scheduled_task)
    print("✅ Scheduler started. Running agent at 10:00 AM daily.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    start_scheduler()
