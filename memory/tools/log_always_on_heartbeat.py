from datetime import datetime
from pathlib import Path

log_dir = Path("/home/rafa1215/memory/logs/always_on")
log_dir.mkdir(parents=True, exist_ok=True)

log_filename = f"heartbeat_{datetime.now().strftime('%Y-%m-%d')}.md"
log_path = log_dir / log_filename

entry = "✅ {} - [Always-On Process Monitor] Log written successfully.\n".format(
    datetime.now().strftime('%Y-%m-%d %I:%M %p'))

with open(log_path, "a") as f:
    f.write(entry)
