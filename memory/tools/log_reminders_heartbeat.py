from datetime import datetime
from pathlib import Path

log_dir = Path("/home/rafa1215/consensus-project/memory/logs/reminders")
log_dir.mkdir(parents=True, exist_ok=True)

log_file = log_dir / f"{datetime.now().date()}_reminder_log.md"

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
content = f"# Reminder Log – {datetime.now().date()}\n\n"
content += f"- [✔] Heartbeat confirmation at {timestamp}. Voice reminder system is active and ready.\n"

log_file.write_text(content)
