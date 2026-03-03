#!/usr/bin/env python3
import re
import sys
from datetime import datetime
from pathlib import Path

MEM_ROOT = Path("/home/rafa1215/memory")
REPO_ROOT = Path("/home/rafa1215/consensus-project")

def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def append_line(p: Path, line: str):
    ensure_dir(p.parent)
    with p.open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")

def mirror(mem_path: Path) -> Path:
    rel = mem_path.relative_to(MEM_ROOT)
    repo_path = REPO_ROOT / "memory" / rel
    ensure_dir(repo_path.parent)
    repo_path.write_text(mem_path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    return repo_path

def kv(arg: str):
    if "=" not in arg:
        return None, None
    k, v = arg.split("=", 1)
    return k.strip().lower(), v.strip()

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 tools/quick_log.py steps=1234 | laps=50 | candidate="Movie (Year)"')
        sys.exit(2)

    k, v = kv(sys.argv[1])
    if not k:
        sys.exit("ERROR: expected key=value")

    ts = now_iso()
    today = datetime.now().date().isoformat()

    if k == "steps":
        if not re.fullmatch(r"\d{1,7}", v):
            sys.exit("ERROR: steps must be an integer")
        p = MEM_ROOT / "logs/fitness" / f"daily_{today}.md"
        append_line(p, f"- {ts} steps={v}")
        rp = mirror(p)
        print(f"OK: {p} (mirrored -> {rp})")
        return

    if k == "laps":
        if not re.fullmatch(r"\d{1,4}", v):
            sys.exit("ERROR: laps must be an integer")
        p = MEM_ROOT / "logs/fitness" / f"daily_{today}.md"
        append_line(p, f"- {ts} laps={v}")
        rp = mirror(p)
        print(f"OK: {p} (mirrored -> {rp})")
        return

    if k == "candidate":
        title = v.strip().strip('"').strip("'").strip()
        if not title:
            sys.exit("ERROR: candidate title is empty")
        p = MEM_ROOT / "logs/system/predictions" / f"candidates_{today}.md"
        append_line(p, f"- {ts} candidate: {title}")
        rp = mirror(p)
        print(f"OK: {p} (mirrored -> {rp})")
        return

    sys.exit("ERROR: key must be steps, laps, or candidate")

if __name__ == "__main__":
    main()
