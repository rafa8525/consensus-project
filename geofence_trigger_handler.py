import datetime
from pathlib import Path

def log_geofence_trigger(location):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/reminders")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    if location.lower() in ["target", "walmart", "costco"]:
        action = "Displayed shopping list"
    elif location.lower() in ["pool", "park", "gym"]:
        action = "Suggested workout: swim or walk"
    else:
        action = "No trigger matched"

    entry = f"{timestamp} — Location: {location} — Action: {action}\n"
    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example: mock location "Target"
    log_geofence_trigger("Target")
