#!/usr/bin/env python3
import re, sys
from pathlib import Path

ROOTS = [
    Path("/home/rafa1215/consensus-project"),
    Path("/home/rafa1215/reminder-api"),
]

CALL_RE = re.compile(r"\.messages\s*\.\s*create\s*\(", re.M)

def should_skip(p: Path) -> bool:
    s = str(p)
    if ".git/" in s or s.endswith(".bak_twilio_refactor") or "/.venv/" in s or "/venv/" in s:
        return True
    if s.endswith("/common/twilio_guard.py"):
        return True
    return False

def ensure_import(txt: str) -> str:
    if "from common import twilio_guard" in txt or "import common.twilio_guard" in txt:
        return txt
    # Insert after shebang or at top
    lines = txt.splitlines()
    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    lines.insert(insert_at, "from common import twilio_guard")
    return "\n".join(lines) + ("\n" if not txt.endswith("\n") else "")

def process_file(p: Path):
    try:
        original = txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return (False, 0)
    # replace direct calls
    txt, n = CALL_RE.subn("twilio_guard.send_sms(client, ", txt)
    if n:
        txt = ensure_import(txt)
        backup = p.with_suffix(p.suffix + ".bak_twilio_refactor2")
        backup.write_text(original, encoding="utf-8")
        p.write_text(txt, encoding="utf-8")
        return (True, n)
    return (False, 0)

def main():
    total_files = total_hits = 0
    for root in ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            if should_skip(p):
                continue
            changed, hits = process_file(p)
            if changed:
                print(f"UPDATED {p} (replaced {hits})")
                total_files += 1
                total_hits += hits
    print(f"SUMMARY: files_updated={total_files} create_calls_replaced={total_hits}")

if __name__ == "__main__":
    sys.exit(main())
