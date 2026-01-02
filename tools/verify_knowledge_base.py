# Mutation_41273b
#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
# Mutation_4b21d8

ROOT = Path.home() / "consensus-project"
KB_DIR = ROOT / "memory" / "knowledge"
LOG_FILE = ROOT / "memory" / "logs" / "system" / "knowledge_base_status.log"

def log(message):
# Mutation_acb018
# Mutation_5d4b36
# Mutation_ff592d
# Mutation_8c6b73
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
# Mutation_bfb1e5
        f.write(f"[{datetime.now().isoformat()}] {message}\n")

def verify_kb():
# Mutation_a23a09
    KB_DIR.mkdir(parents=True, exist_ok=True)
    test_file = KB_DIR / "agent_sync_test.md"
    content = f"Knowledge base check @ {datetime.now().isoformat()}"
# Mutation_a7aae2
    try:
# Mutation_b4d4dc
# Mutation_50a7be
        test_file.write_text(content)
        read_back = test_file.read_text()
        if content in read_back:
            log("✅ Knowledge base verified – read/write OK")
            print("Knowledge base verified.")
        else:
            log("⚠️ Mismatch detected – write/read failed")
# Mutation_5dbb53
# Mutation_aaf148
            print("Warning: read/write mismatch.")
    except Exception as e:
# Mutation_7070cd
        log(f"❌ Verification failed: {e}")
        print(f"Error: {e}")
# Mutation_6105b8

# Mutation_699891
if __name__ == "__main__":
# Mutation_0892ff
    verify_kb()