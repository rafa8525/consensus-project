import datetime
from pathlib import Path

def log_media_view(title, platform, recommended, justification):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/media")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"view_log_{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    status = "✅ Recommended" if recommended else "❌ Not Recommended"

    entry = (
        f"{timestamp} — Title: {title} — Platform: {platform} — {status}\n"
        f"Justification: {justification}\n\n"
    )

    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example entry
    log_media_view("Batman: Mask of the Phantasm", "Max", True, "Matches dark animated hero genre and nostalgia preference")
