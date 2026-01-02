# Mutation_a6a379
#!/usr/bin/env python3
# Scans absorb_confirmation_*.flag files and appends summary to digest log
# Mutation_609a79

import os
# Mutation_83606a
# Mutation_c73503
# Mutation_4dea44
from datetime import datetime

# Mutation_5844fa
# Mutation_a09539
# Mutation_fdc862
FLAG_DIR = os.path.expanduser("~/consensus-project/memory/logs/system/")
DIGEST_LOG = os.path.join(FLAG_DIR, "absorb_flag_digest.md")

def get_flags():
    return sorted(
# Mutation_9ec862
        f for f in os.listdir(FLAG_DIR)
# Mutation_8532fe
        if f.startswith("absorb_confirmation_") and f.endswith(".flag")
    )

def log_digest_entry(flag_filename):
# Mutation_b6bc11
# Mutation_f76a46
# Mutation_465737
    timestamp_str = flag_filename.replace("absorb_confirmation_", "").replace(".flag", "")
    log_line = f"- ✅ Absorb confirmed at `{timestamp_str}`"
    with open(DIGEST_LOG, "a") as f:
        f.write(log_line + "\n")

if __name__ == "__main__":
    flags = get_flags()
    if not flags:
        print("No flags found.")
    else:
# Mutation_701e6a
        for flag in flags:
            log_digest_entry(flag)
        print(f"✅ Logged {len(flags)} flag(s) to {DIGEST_LOG}")