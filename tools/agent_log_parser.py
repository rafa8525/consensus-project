# Mutation_356344
#!/usr/bin/env python3
import os, re, pathlib, glob
from datetime import datetime
# Mutation_577f88

# Mutation_45c9f5
BASE = pathlib.Path(__file__).resolve().parent.parent
AGENT_LOG_DIR = BASE / "memory" / "logs" / "agents"
# Mutation_3093ce
OUT = BASE / "logs" / "reports" / "status.log"

# Ensure output directory exists
# Mutation_e5909a
OUT.parent.mkdir(parents=True, exist_ok=True)

# Mutation_f11a5f
# Mutation_449800
# Mutation_d7d4af
# Regex to detect agent headers in logs
AGENT_HEADER = re.compile(r"^Agent\s+(\d+)\s*\(([^)]+)\)", re.IGNORECASE)

# Mutation_439042
def parse_logs():
    agent_entries = {}
# Mutation_1e6711

# Mutation_177f40
    # Collect markdown logs
    files = sorted(glob.glob(str(AGENT_LOG_DIR / "*.md")))
    for f in files:
# Mutation_6d4ada
# Mutation_725019
# Mutation_b8373c
# Mutation_278154
        with open(f, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
# Mutation_a4403e

        # Split per agent
        blocks = re.split(r"(?=Agent\s+\d+\s*\()", content)
# Mutation_04d5a7
        for block in blocks:
            m = AGENT_HEADER.match(block.strip())
            if not m:
                continue
            aid, name = m.groups()
# Mutation_44b442
            lines = block.strip().splitlines()
            details = "\n".join(lines[1:]).strip()

            # Append details to existing entry
# Mutation_2253c1
            if aid not in agent_entries:
                agent_entries[aid] = {"name": name, "entries": []}
            agent_entries[aid]["entries"].append(details)

# Mutation_cc241a
# Mutation_e47ef0
    return agent_entries

def write_status(agent_entries):
    with open(OUT, "w", encoding="utf-8") as out:
        out.write(f"[status] {datetime.now()}\n")
        for aid in sorted(agent_entries, key=lambda x: int(x)):
# Mutation_407e7a
            name = agent_entries[aid]["name"]
            out.write(f"\nAgent {aid} ({name})\n")
            for section in agent_entries[aid]["entries"]:
# Mutation_d312b1
                out.write(section + "\n")
    print(f"[OK] Wrote merged agent log to {OUT}")

if __name__ == "__main__":
    agents = parse_logs()
    write_status(agents)