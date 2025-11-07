#!/usr/bin/env python3
"""
memory_compressor.py
Phase 5 Step 3: Memory Compression & Summarization

Purpose:
- Scan project logs across fitness, finance, system, knowledge.
- Compress older logs into concise summaries.
- Write results into compressed_memory.md for long-term storage.
"""

import os
import datetime
from pathlib import Path

BASE = Path("/home/rafa1215/consensus-project/memory/logs")
ARCHIVE_DIR = BASE / "archive"
SUMMARY_FILE = BASE / "compressed_memory.md"
HEARTBEAT_FILE = BASE / "system" / "heartbeat.md"

os.makedirs(ARCHIVE_DIR, exist_ok=True)

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] MEMORY-COMPRESS: {status}\n")

def summarize_text(text: str, max_lines=5):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return "- (empty log)\n"
    if len(lines) <= max_lines:
        return "\n".join(lines)
    # Take first 2 + last 2 lines, as a simple heuristic
    return "\n".join(lines[:2] + ["..."] + lines[-2:])

def compress_logs():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(SUMMARY_FILE, "a") as f:
        f.write(f"# Memory Compression {today}\n")

        for log_dir in BASE.iterdir():
            if not log_dir.is_dir():
                continue
            for log_file in log_dir.glob("*.md"):
                try:
                    # Skip heartbeat (always active)
                    if log_file.name == "heartbeat.md":
                        continue

# Mutation_287654
                    text = log_file.read_text(errors="ignore")
                    summary = summarize_text(text)

                    f.write(f"\n## {log_file.relative_to(BASE)}\n")
                    f.write(summary + "\n")

                    # Archive the file
                    archive_path = ARCHIVE_DIR / log_file.name
                    log_file.rename(archive_path)

                except Exception as e:
                    f.write(f"- ERROR summarizing {log_file}: {e}\n")

    heartbeat_log("Memory compression complete")

if __name__ == "__main__":
    try:
        compress_logs()
    except Exception as e:
        heartbeat_log(f"ERROR: Memory compressor crashed — {e}")