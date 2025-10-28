#!/usr/bin/env python3
"""
log_initializer.py
Create placeholder log files for all agents listed in roles.csv
"""

import os
import csv
from datetime import datetime

ROLES_CSV = "memory/agents/roles.csv"
BASE_DIR = os.path.expanduser("~/consensus-project")
TS = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
REPORT = os.path.join(BASE_DIR, "memory/logs/system/log_initializer_report.md")

def ensure_file(path, agent, role):
    """Create the file if missing, with a timestamp header"""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Initialized log for {agent}\n")
            f.write(f"# Role: {role}\n")
            f.write(f"# Created: {TS}\n\n")
        return True
    return False

def main():
    created = []
    skipped = []
    roles_path = os.path.join(BASE_DIR, ROLES_CSV)

    if not os.path.exists(roles_path):
        print(f"❌ roles.csv not found at {roles_path}")
        return

    with open(roles_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            agent = row["Agent"].strip()
            role = row["Role"].strip()
            expected = os.path.join(BASE_DIR, row["ExpectedPath"].strip())
            if ensure_file(expected, agent, role):
                created.append(expected)
            else:
                skipped.append(expected)

    # Write report
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "a", encoding="utf-8") as f:
        f.write(f"\n[{TS}] Log initializer run\n")
        for c in created:
            f.write(f"✅ Created: {c}\n")
        for s in skipped:
            f.write(f"⏩ Skipped (already exists): {s}\n")

    print(f"✅ Done. Created {len(created)} new logs, skipped {len(skipped)}.")

if __name__ == "__main__":
    main()
