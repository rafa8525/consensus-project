#!/usr/bin/env python3
"""
role_checker_agent.py
Audits coverage of agents defined in roles.csv.
Checks if ExpectedPath exists and logs results.
"""

import csv
import os
from datetime import datetime

ROLES_FILE = "memory/agents/roles.csv"
REPORT_FILE = "memory/logs/system/role_checker_report.md"


def log_report(lines):
    """Write report lines to role_checker_report.md"""
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n## Role Check Report @ {ts}\n")
        for line in lines:
            f.write(f"{line}\n")


def check_roles():
    if not os.path.exists(ROLES_FILE):
        log_report([f"❌ roles.csv not found at {ROLES_FILE}"])
        return

    with open(ROLES_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        results = []
        for row in reader:
            agent = row["Agent"]
            role = row["Role"]
            path = row["ExpectedPath"]

            if os.path.exists(path):
                results.append(f"✅ {agent} ({role}) → {path}")
            else:
                results.append(f"⚠️ {agent} ({role}) → Missing {path}")

        log_report(results)


def main():
    log_report(["🚀 role_checker_agent.py started"])
    check_roles()


if __name__ == "__main__":
    main()
