#!/usr/bin/env python3
"""
agents_recommendation.py
Scan system/heartbeat logs for issues and map them to responsible agents
based on roles.csv. Now prioritizes file/path matches over loose keywords.
"""

import os
import re
import csv
import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROLES_FILE = BASE / "memory/agents/roles.csv"
LOG_DIRS = [
    BASE / "memory/logs/system",
    BASE / "memory/logs/heartbeat",
]

OUT_FILE = BASE / "memory/logs/system/agent_recommendations.md"
CUTOFF_HOURS = 48


def load_roles():
    roles = []
    with open(ROLES_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            roles.append(
                {
                    "agent": row["Agent"].strip(),
                    "responsibility": row["Role"].strip(),
                    "path": row["ExpectedPath"].strip(),
                }
            )
    return roles


def map_to_agent(message, roles):
    """Match issue message to a responsible agent, preferring explicit path matches."""
    msg = message.lower()

    # 1. Strong: check for direct file/path mentions
    for role in roles:
        path = role.get("path", "").lower()
        if path and any(part in msg for part in path.split("/")):
            return role["agent"]

    # Special case: master control loop
    if "master_control_loop.py" in msg or "mcl" in msg:
        return "AI_MCL"

    # 2. Fallback: keyword token matching
    for role in roles:
        tokens = re.split(r"[,\s]+", role["responsibility"])
        tokens = [t.strip().lower() for t in tokens if t.strip()]
        for token in tokens:
            if token and token in msg:
                return role["agent"]

    return "Unassigned"


def scan_file(filepath, cutoff):
    issues = []
    if not filepath.exists():
        return issues
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if re.search(r"error|missing|failed|cannot|no such file|rc=", line, re.IGNORECASE):
                    # crude timestamp extraction
                    ts = datetime.datetime.fromtimestamp(filepath.stat().st_mtime)
                    if ts < cutoff:
                        continue
                    issues.append(line)
    except Exception as e:
        issues.append(f"[scanner] failed reading {filepath}: {e}")
    return issues


def main():
    roles = load_roles()
    cutoff = datetime.datetime.now() - datetime.timedelta(hours=CUTOFF_HOURS)
    all_issues = []

    for logdir in LOG_DIRS:
        if not logdir.exists():
            continue
        for f in logdir.glob("*.log*"):
            all_issues.extend(scan_file(f, cutoff))

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as out:
        for issue in all_issues:
            agent = map_to_agent(issue, roles)
            out.write(f"- {issue}\n⚠️ Recommendation ({agent}): { 'Check logs' if agent!='Unassigned' else 'Missing file/agent' }\n")

    print(f"✅ Recommendations written to {OUT_FILE}")


if __name__ == "__main__":
    main()
