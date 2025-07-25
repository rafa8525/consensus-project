from datetime import datetime
import os

log_dir = "/home/rafa1215/consensus-project/memory/logs/geofencing"
os.makedirs(log_dir, exist_ok=True)

today_str = datetime.now().strftime("%Y-%m-%d")
log_file_path = os.path.join(log_dir, f"{today_str}.md")

simulated_events = [
    {"time": "07:45 AM", "event": "Detected SSID: Kitchen-WiFi", "action": "Entered kitchen"},
    {"time": "08:10 AM", "event": "Detected SSID: BART-WiFi", "action": "Entered Pittsburg BART station"},
    {"time": "08:50 AM", "event": "No new geofence triggers", "action": "Idle log update"}
]

lines = [f"# Geofencing Log – {today_str}\n", "---\n"]
for event in simulated_events:
    lines.append(f"- **{event['time']}** – {event['event']} → *{event['action']}*\n")

with open(log_file_path, "w") as f:
    f.writelines(lines)
