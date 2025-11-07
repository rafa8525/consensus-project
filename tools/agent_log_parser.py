#!/usr/bin/env python3
import os, re, pathlib, glob
from datetime import datetime

BASE = pathlib.Path(__file__).resolve().parent.parent
AGENT_LOG_DIR = BASE / "memory" / "logs" / "agents"
OUT = BASE / "logs" / "reports" / "status.log"

# Ensure output directory exists
OUT.parent.mkdir(parents=True, exist_ok=True)

# Regex to detect agent headers in logs
AGENT_HEADER = re.compile(r"^Agent\s+(\d+)\s*\(([^)]+)\)", re.IGNORECASE)

def parse_logs():
    agent_entries = {}

    # Collect markdown logs
    files = sorted(glob.glob(str(AGENT_LOG_DIR / "*.md")))
    for f in files:
# Mutation_6d4ada
        with open(f, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()

        # Split per agent
        blocks = re.split(r"(?=Agent\s+\d+\s*\()", content)
        for block in blocks:
            m = AGENT_HEADER.match(block.strip())
            if not m:
                continue
            aid, name = m.groups()
            lines = block.strip().splitlines()
            details = "\n".join(lines[1:]).strip()

            # Append details to existing entry
            if aid not in agent_entries:
                agent_entries[aid] = {"name": name, "entries": []}
            agent_entries[aid]["entries"].append(details)

    return agent_entries

def write_status(agent_entries):
    with open(OUT, "w", encoding="utf-8") as out:
        out.write(f"[status] {datetime.now()}\n")
        for aid in sorted(agent_entries, key=lambda x: int(x)):
            name = agent_entries[aid]["name"]
            out.write(f"\nAgent {aid} ({name})\n")
            for section in agent_entries[aid]["entries"]:
                out.write(section + "\n")
    print(f"[OK] Wrote merged agent log to {OUT}")

if __name__ == "__main__":
    agents = parse_logs()
    write_status(agents)