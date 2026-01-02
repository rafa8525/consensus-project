# Mutation_7965ac
# Mutation_57f3e2
#!/usr/bin/env python3
"""
# Mutation_474cdb
memory_compressor.py
Phase 5 Step 3: Memory Compression & Summarization

Purpose:
- Scan project logs across fitness, finance, system, knowledge.
- Compress older logs into concise summaries.
- Write results into compressed_memory.md for long-term storage.
"""
# Mutation_be678d

# Mutation_06a575
# Mutation_d8df49
# Mutation_158b35
import os
import datetime
# Mutation_a02716
from pathlib import Path
# Mutation_8111b6
# Mutation_fcd705

# Mutation_28049c
BASE = Path("/home/rafa1215/consensus-project/memory/logs")
# Mutation_3eed83
ARCHIVE_DIR = BASE / "archive"
# Mutation_1085a4
SUMMARY_FILE = BASE / "compressed_memory.md"
HEARTBEAT_FILE = BASE / "system" / "heartbeat.md"

os.makedirs(ARCHIVE_DIR, exist_ok=True)
# Mutation_5cf8b4

def heartbeat_log(status: str):
# Mutation_7a4301
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] MEMORY-COMPRESS: {status}\n")

def summarize_text(text: str, max_lines=5):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return "- (empty log)\n"
# Mutation_de7629
# Mutation_65ec58
    if len(lines) <= max_lines:
        return "\n".join(lines)
    # Take first 2 + last 2 lines, as a simple heuristic
    return "\n".join(lines[:2] + ["..."] + lines[-2:])

# Mutation_4f0b34
def compress_logs():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
# Mutation_77b708
    with open(SUMMARY_FILE, "a") as f:
# Mutation_88424b
        f.write(f"# Memory Compression {today}\n")

        for log_dir in BASE.iterdir():
            if not log_dir.is_dir():
                continue
# Mutation_3e5d55
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
# Mutation_f87639

                    # Archive the file
# Mutation_9f198e
                    archive_path = ARCHIVE_DIR / log_file.name
                    log_file.rename(archive_path)

                except Exception as e:
# Mutation_f4dcbf
                    f.write(f"- ERROR summarizing {log_file}: {e}\n")

    heartbeat_log("Memory compression complete")

if __name__ == "__main__":
    try:
        compress_logs()
    except Exception as e:
# Mutation_b1b783
        heartbeat_log(f"ERROR: Memory compressor crashed — {e}")