import datetime
import traceback
from pathlib import Path
from gmail_utils import get_gmail_service

BASE = Path("/home/rafa1215/consensus-project")
LOG_FILE = BASE / "memory/logs/email/voice_gmail_handler.log"

def log(msg: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

def read_latest_email(max_results=1):
    try:
        service = get_gmail_service()
        log("🔍 Fetching latest email(s)...")

        result = (
            service.users()
            .messages()
            .list(userId="me", maxResults=max_results, labelIds=["INBOX"])
            .execute()
        )
        messages = result.get("messages", [])
        if not messages:
            return "No new messages found."

        msg_id = messages[0]["id"]
        msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        headers = msg["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown Sender)")
        snippet = msg.get("snippet", "")[:400]

        summary = f"Latest email from {sender} with subject '{subject}': {snippet}"
        log(f"✅ Retrieved: {summary}")
        return summary

    except Exception as e:
        log(f"❌ Failed to fetch Gmail: {e}\n{traceback.format_exc()}")
        return "An error occurred while accessing your Gmail."

def handle_voice_command(command: str):
    log(f"🎤 Voice command received: {command}")
    cmd = command.lower()
    if "latest email" in cmd or "read my email" in cmd:
        return read_latest_email()
    elif "summarize" in cmd or "email summary" in cmd:
        return read_latest_email(3)
    else:
        return "Command not recognized for Gmail voice handler."

if __name__ == "__main__":
    print(handle_voice_command("Read my latest email"))
