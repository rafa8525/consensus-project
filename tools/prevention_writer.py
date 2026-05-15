#!/usr/bin/env python3
"""
prevention_writer.py

Create a prevention note and maintain a simple prevention index.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


LOCAL_TZ = ZoneInfo("America/Los_Angeles")


def slugify(text: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in text.strip())
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")[:80] or "issue"


def ensure_index(index_path: Path) -> None:
    if not index_path.exists():
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(
            "# Prevention Index\n\n"
            "| Date | Issue | File |\n"
            "|---|---|---|\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a prevention note.")
    parser.add_argument("--mem-root", default="/home/rafa1215/memory")
    parser.add_argument("--issue", required=True)
    parser.add_argument("--root-cause", required=True)
    parser.add_argument("--fix", required=True)
    parser.add_argument("--prevention-rule", required=True)
    parser.add_argument("--owner", default="Master Decision Agent")
    parser.add_argument("--verify", default="python3 -m py_compile <file>")
    args = parser.parse_args()

    mem_root = Path(args.mem_root)
    prevention_dir = mem_root / "logs" / "prevention"
    prevention_dir.mkdir(parents=True, exist_ok=True)

    now_local = datetime.now(LOCAL_TZ)
    date_str = now_local.date().isoformat()
    slug = slugify(args.issue)
    note_path = prevention_dir / f"{date_str}_{slug}.md"
    index_path = prevention_dir / "prevention_index.md"

    ensure_index(index_path)

    body = (
        f"# Prevention Note\n"
        f"- Date: {now_local.isoformat()}\n"
        f"- Issue: {args.issue}\n"
        f"- Owner: {args.owner}\n\n"
        f"## Root Cause\n"
        f"{args.root_cause}\n\n"
        f"## Fix\n"
        f"{args.fix}\n\n"
        f"## Prevention Rule\n"
        f"{args.prevention_rule}\n\n"
        f"## Verification Command\n"
        f"`{args.verify}`\n"
    )
    note_path.write_text(body, encoding="utf-8")

    with index_path.open("a", encoding="utf-8") as fh:
        fh.write(f"| {date_str} | {args.issue} | {note_path.name} |\n")

    print(note_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())