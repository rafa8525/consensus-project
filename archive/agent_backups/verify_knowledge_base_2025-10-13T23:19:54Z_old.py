#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

ROOT = Path.home() / "consensus-project"
KB_DIR = ROOT / "memory" / "knowledge"
LOG_FILE = ROOT / "memory" / "logs" / "system" / "knowledge_base_status.log"

def log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")

def verify_kb():
    KB_DIR.mkdir(parents=True, exist_ok=True)
    test_file = KB_DIR / "agent_sync_test.md"
    content = f"Knowledge base check @ {datetime.now().isoformat()}"
    try:
        test_file.write_text(content)
        read_back = test_file.read_text()
        if content in read_back:
            log("✅ Knowledge base verified – read/write OK")
            print("Knowledge base verified.")
        else:
            log("⚠️ Mismatch detected – write/read failed")
            print("Warning: read/write mismatch.")
    except Exception as e:
        log(f"❌ Verification failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_kb()
