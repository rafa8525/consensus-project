import datetime
from pathlib import Path

def log_points(activity, value):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/fitness")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"reward_points_{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    points = 0
    activity = activity.lower()

    if activity == "meal":
        points = 5
    elif activity == "barcode":
        points = 2
    elif activity == "swim":
        points = value // 5  # 1 point per 5 laps
    elif activity == "steps":
        points = value // 1000  # 1 point per 1,000 steps
    else:
        return

    entry = f"{timestamp} — Activity: {activity} — Value: {value} — Points: {points}\n"
    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example: log 30 swim laps
    log_points("swim", 30)
