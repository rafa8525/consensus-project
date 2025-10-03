#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

ROOT = Path("/home/rafa1215/consensus-project")
OUT  = ROOT / "memory" / "logs" / "status" / "progress_snapshot.md"

SOURCES = [
    ROOT / "progress_evaluation_plan.txt",
    ROOT / "AI Consensus System Project.txt",
    ROOT / "AI_Consensus_System_Unified_Prompt.txt",
]

def main():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"# Progress Snapshot — {ts}", ""]
    for s in SOURCES:
        status = "FOUND" if s.exists() else "MISSING"
        size = s.stat().st_size if s.exists() else 0
        lines += [
            f"## {s.name}",
            f"- Path: {s}",
            f"- Status: **{status}**",
            f"- Size: {size} bytes",
            ""
        ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print("✅ Wrote", OUT)

if __name__ == "__main__":
    main()
