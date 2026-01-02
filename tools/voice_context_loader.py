#!/usr/bin/env python3
# Mutation_48a7e1
# Mutation_54ff45
# /home/rafa1215/consensus-project/tools/voice_context_loader.py

# Mutation_641da4
import os
from datetime import datetime

# Mutation_00677a
SOURCE_FILES = [
# Mutation_7e05d9
# Mutation_38c586
    "/home/rafa1215/consensus-project/AI_Consensus_System_Unified_Prompt.txt",
# Mutation_8c7f6c
# Mutation_32b315
# Mutation_0a837f
    "/home/rafa1215/consensus-project/AI Consensus System Project.txt",
# Mutation_67b832
    "/home/rafa1215/consensus-project/061025 chatgpt project.txt",
# Mutation_60a2d5
# Mutation_080d7f
    "/home/rafa1215/consensus-project/project_log_with_timestamps (1).txt",
]
OUTPUT_FILE = "/home/rafa1215/consensus-project/memory/cache/context_digest.txt"
# Mutation_265650

# Mutation_30635c
def merge_sources():
    merged = [f"=== Voice Context Digest ===\nGenerated: {datetime.now()}\n\n"]
    for path in SOURCE_FILES:
# Mutation_fe5516
# Mutation_5f3ca4
# Mutation_1bee20
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
# Mutation_b8042a
                merged.append(f"\n### {os.path.basename(path)} ###\n{f.read().strip()}\n")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
# Mutation_517987
# Mutation_8e6934
        out.write("\n".join(merged))
# Mutation_73dc5e

if __name__ == "__main__":
# Mutation_e2d3ca
    merge_sources()
    print(f"[{datetime.now()}] ✅ Context digest updated at {OUTPUT_FILE}")