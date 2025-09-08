import os
from datetime import datetime

# Only run every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
hour = datetime.utcnow().hour
if hour not in [0, 6, 12, 18]:
    print(f"⏸️ Skipping — not a 6-hour heartbeat slot. (Current UTC hour: {hour})")
    exit()

log_folders = ["system", "twilio", "fitness", "transport", "nutrition", "geofencing"]
base_path = "/home/rafa1215/consensus-project/memory/logs"

now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
filename = datetime.utcnow().strftime("heartbeat_%Y-%m-%d.md")
message = f"✅ Agent heartbeat — {now}\n"

for folder in log_folders:
    full_path = os.path.join(base_path, folder, filename)
    with open(full_path, "a") as f:
        f.write(message)

print("✅ Heartbeat logs written.")
