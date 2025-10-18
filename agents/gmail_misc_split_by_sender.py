#!/usr/bin/env python3
"""
gmail_misc_split_by_sender.py
Splits misc_sorted_merged.md into individual Markdown files per sender.
No Gmail access — local only.
"""

import os
import re

# === CONFIG ===
MERGED_FILE = os.path.expanduser(
    "~/consensus-project/memory/logs/email/misc_sorted_merged.md"
)
OUTPUT_DIR = os.path.expanduser(
    "~/consensus-project/memory/logs/email/senders/"
)

def sanitize_filename(name: str) -> str:
    """Convert sender name/email into a safe filename."""
    clean = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", name)
    clean = re.sub(r'\s+', "_", clean)
    return clean[:80]  # limit length

def split_by_sender():
    if not os.path.exists(MERGED_FILE):
        print(f"⚠️ File not found: {MERGED_FILE}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"📂 Splitting {MERGED_FILE} into per-sender files…")

    with open(MERGED_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_sender = None
    buffer = []

    for line in lines:
        if line.startswith("## "):
            # Save previous sender section
            if current_sender and buffer:
                safe_name = sanitize_filename(current_sender)
                out_path = os.path.join(OUTPUT_DIR, f"{safe_name}.md")
                with open(out_path, "w", encoding="utf-8") as out:
                    out.writelines(buffer)
                print(f"✅ Wrote {out_path} ({len(buffer)} lines)")
                buffer.clear()
            current_sender = line[3:].strip()
            buffer.append(line)
        elif current_sender:
            buffer.append(line)

    # Write last sender
    if current_sender and buffer:
        safe_name = sanitize_filename(current_sender)
        out_path = os.path.join(OUTPUT_DIR, f"{safe_name}.md")
        with open(out_path, "w", encoding="utf-8") as out:
            out.writelines(buffer)
        print(f"✅ Wrote {out_path} ({len(buffer)} lines)")

    print(f"\n🏁 Done. Files saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    split_by_sender()
