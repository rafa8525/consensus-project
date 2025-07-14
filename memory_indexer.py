import os
import json
from pathlib import Path

MEMORY_ROOT = Path("memory")
INDEX_FILE = MEMORY_ROOT / "index" / "memory_word_index.json"

def build_index():
    if not MEMORY_ROOT.exists():
        print(f"❌ Memory folder not found at {MEMORY_ROOT}")
        return

    index = {}
    for file_path in MEMORY_ROOT.rglob("*"):
        if file_path.is_file() and file_path.suffix in [".md", ".txt", ".log"]:
            try:
                index[str(file_path.relative_to(MEMORY_ROOT))] = file_path.read_text()
            except Exception as e:
                print(f"⚠️ Could not read {file_path}: {e}")

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)
    print(f"✅ Indexed {len(index)} files into {INDEX_FILE}")

if __name__ == "__main__":
    build_index()