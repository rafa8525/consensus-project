#!/usr/bin/env python3
"""
gmail_misc_merge_batches.py
Merges multiple batch-sorted Gmail 'Misc' logs into one file,
removes duplicates, and sorts alphabetically by sender.
"""

import os
import glob

# === CONFIG ===
BATCH_PATH = os.path.expanduser("~/consensus-project/memory/logs/email/")
MERGED_OUTPUT = os.path.join(BATCH_PATH, "misc_sorted_merged.md")

def merge_batches():
    # Find all misc_sorted_batch*.md files
    batch_files = sorted(glob.glob(os.path.join(BATCH_PATH, "misc_sorted_batch*.md")))
    if not batch_files:
        print("⚠️ No batch files found.")
        return

    print(f"🔍 Found {len(batch_files)} batch files to merge.")
    lines = []
    for file_path in batch_files:
        with open(file_path, "r", encoding="utf-8") as f:
            lines.extend(f.readlines())

    # Remove duplicates while preserving order
    seen = set()
    deduped = []
    for line in lines:
        if line.strip() not in seen:
            deduped.append(line)
            seen.add(line.strip())

    # Sort alphabetically by sender headers
    sorted_lines = sorted(
        [ln for ln in deduped if ln.startswith("## ")],
        key=lambda s: s.lower()
    )

    # Reassemble the markdown file
    with open(MERGED_OUTPUT, "w", encoding="utf-8") as f:
        f.write("# Misc Folder – Fully Merged and Sorted Alphabetically\n\n")
        for line in sorted_lines:
            f.write(line)
            # find associated details following each sender
            sender = line.strip()
            for subline in deduped:
                if not subline.startswith("## ") and sender in subline:
                    f.write(subline)
            f.write("\n")

    print(f"✅ Merged and sorted successfully.")
    print(f"📄 Output saved to: {MERGED_OUTPUT}")

if __name__ == "__main__":
    merge_batches()
