import os
from datetime import datetime, timezone

HEARTBEAT_LOG = os.path.expanduser("~/consensus-project/memory/logs/system/voice_trigger_heartbeat.log")
NOW = datetime.now(timezone.utc).isoformat()

def already_logged_today():
    if not os.path.exists(HEARTBEAT_LOG):
        return False
    with open(HEARTBEAT_LOG, "r") as f:
        return NOW[:10] in f.read()  # Check for today’s date

def write_heartbeat():
    entry = (
        f"# Voice Trigger Fallback Check\n"
        f"**Timestamp:** {NOW}\n"
        f"**Check:** Monitoring fallback for undelivered SMS after /voice_trigger.\n"
        f"**Result:** Placeholder entry created.\n\n"
    )
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(entry)
    print("✅ Voice fallback heartbeat logged.")

def main():
    if already_logged_today():
        print("⏭️ Fallback already logged today.")
    else:
        write_heartbeat()

if __name__ == "__main__":
    main()
