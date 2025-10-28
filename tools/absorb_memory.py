#!/usr/bin/env python3
import os
import sys
import datetime
import traceback

MEMORY_DIR = "/home/rafa1215/consensus-project/memory/"
LOG_PATH = "/home/rafa1215/consensus-project/memory/logs/system/absorb_memory.log"

def log(msg):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

def should_skip(file_path):
    # Skip flag files, logs, binary or non-markdown text
    return (
        file_path.endswith(".flag") or
        file_path.endswith(".log") or
        os.path.basename(file_path).startswith(".") or
        os.path.getsize(file_path) > 5_000_000  # skip huge files >5MB
    )

def absorb_memory():
    try:
        log("🧠 Starting full memory absorption cycle...")
        total, indexed, failed = 0, 0, 0

        for root, dirs, files in os.walk(MEMORY_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                if should_skip(file_path):
                    continue

                total += 1
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        preview = content.strip().replace("\n", " ")[:100]
                        log(f"📄 Indexed: {file_path} | Preview: {preview}")
                        indexed += 1
                except Exception as e:
                    log(f"⚠️ Failed to read {file_path}: {str(e)}")
                    failed += 1

        log(f"✅ Absorption complete — Scanned: {total}, Indexed: {indexed}, Failed: {failed}")
        return 0

    except Exception as e:
        log(f"❌ absorb_memory() failed: {str(e)}")
        log(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit(absorb_memory())
