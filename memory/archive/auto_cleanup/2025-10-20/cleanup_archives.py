#!/usr/bin/env python3
import os
import shutil

# Directories
BASE_DIR = "/home/rafa1215/consensus-project"
SEED_DIR = os.path.join(BASE_DIR, "seed")
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
ARCHIVE_DIR = os.path.join(MEMORY_DIR, "archive")

# Files
redundant_files = [
    "vpn_activation_testing_plan.txt",
    "VPNActivationTestingPlan.txt",
    "VPN_activation_testing.txt"
]
archive_file = "progress_evaluation_plan.txt"

def cleanup_files():
    # Ensure archive directory exists
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
        print(f"Created archive directory: {ARCHIVE_DIR}")

    # Remove redundant VPN files from seed/
    for f in redundant_files:
        path = os.path.join(SEED_DIR, f)
        if os.path.exists(path):
            os.remove(path)
            print(f"Removed redundant file: {path}")
        else:
            print(f"File not found (skipped): {path}")

    # Archive progress evaluation plan from seed/ → memory/archive/
    src = os.path.join(SEED_DIR, archive_file)
    if os.path.exists(src):
        dst = os.path.join(ARCHIVE_DIR, archive_file)
        shutil.move(src, dst)
        print(f"Archived {src} → {dst}")
    else:
        print(f"Archive file not found (skipped): {src}")

if __name__ == "__main__":
    cleanup_files()
