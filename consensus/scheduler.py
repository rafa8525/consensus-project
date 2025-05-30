import schedule
import time
import subprocess
import datetime
import logging
import argparse
import os

# Setup logging
log_filename = f"consensus_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def run_agent():
    goal_file = os.path.join(os.path.dirname(__file__), "scheduled_goal.txt")
    if not os.path.exists(goal_file):
        logging.error("scheduled_goal.txt not found.")
        print("🚫 scheduled_goal.txt not found.")
        return

    with open(goal_file, "r", encoding="utf-8") as f:
        goal = f.read().strip()

    if goal:
        print(f"🚀 Running agent with goal: {goal}")
        logging.info(f"Running agent with goal: {goal}")
        subprocess.run(["python", "consensus/main.py", "--goal", goal])
    else:
        logging.warning("scheduled_goal.txt is empty.")
        print("🚫 scheduled_goal.txt is empty.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-now", action="store_true", help="Run the agent immediately")
    args = parser.parse_args()

    if args.run_now:
        run_agent()
    else:
        print("📆 Scheduler started. Running agent at 10:00 AM daily.")
        schedule.every().day.at("10:00").do(run_agent)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    main()
