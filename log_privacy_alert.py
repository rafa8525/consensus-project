import datetime
from pathlib import Path

def log_privacy_alert(category, message):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/security")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"privacy_alerts_{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    entry = f"{timestamp} — [{category}] {message}\n"
    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example alert
    log_privacy_alert("Warning", "Unencrypted token used for webhook transmission")
