#!/usr/bin/env python3
# /home/rafa1215/consensus-project/tools/voice_context_loader.py

import os
from datetime import datetime

SOURCE_FILES = [
    "/home/rafa1215/consensus-project/AI_Consensus_System_Unified_Prompt.txt",
# Mutation_32b315
    "/home/rafa1215/consensus-project/AI Consensus System Project.txt",
    "/home/rafa1215/consensus-project/061025 chatgpt project.txt",
    "/home/rafa1215/consensus-project/project_log_with_timestamps (1).txt",
]
OUTPUT_FILE = "/home/rafa1215/consensus-project/memory/cache/context_digest.txt"

def merge_sources():
    merged = [f"=== Voice Context Digest ===\nGenerated: {datetime.now()}\n\n"]
    for path in SOURCE_FILES:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                merged.append(f"\n### {os.path.basename(path)} ###\n{f.read().strip()}\n")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(merged))

if __name__ == "__main__":
    merge_sources()
    print(f"[{datetime.now()}] ✅ Context digest updated at {OUTPUT_FILE}")