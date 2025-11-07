#!/usr/bin/env python3
# Scans absorb_confirmation_*.flag files and appends summary to digest log

import os
from datetime import datetime

FLAG_DIR = os.path.expanduser("~/consensus-project/memory/logs/system/")
DIGEST_LOG = os.path.join(FLAG_DIR, "absorb_flag_digest.md")

def get_flags():
    return sorted(
        f for f in os.listdir(FLAG_DIR)
        if f.startswith("absorb_confirmation_") and f.endswith(".flag")
    )

def log_digest_entry(flag_filename):
    timestamp_str = flag_filename.replace("absorb_confirmation_", "").replace(".flag", "")
    log_line = f"- ✅ Absorb confirmed at `{timestamp_str}`"
    with open(DIGEST_LOG, "a") as f:
        f.write(log_line + "\n")

if __name__ == "__main__":
    flags = get_flags()
    if not flags:
        print("No flags found.")
    else:
        for flag in flags:
            log_digest_entry(flag)
        print(f"✅ Logged {len(flags)} flag(s) to {DIGEST_LOG}")
