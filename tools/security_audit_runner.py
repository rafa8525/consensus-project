#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import shutil, os

OUT = Path("/home/rafa1215/consensus-project/memory/logs/security/audit_log.md")

def main():
    total, used, free = shutil.disk_usage("/")
    env_ok = "PATH" in os.environ
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# Mutation_feb1fb
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        f"# Security Audit — {ts}\n"
        f"- Disk usage (GB): total={total/1e9:.2f}, used={used/1e9:.2f}, free={free/1e9:.2f}\n"
        f"- Basic env present: {env_ok}\n"
        f"- Notes: Add specific checks over time (permissions, secrets layout, scheduled tasks).\n"
    )
    print("✅ Wrote", OUT)

if __name__ == "__main__":
    main()