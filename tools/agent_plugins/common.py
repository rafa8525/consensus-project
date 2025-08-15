from pathlib import Path
from datetime import date, datetime, timezone
import json, subprocess

ROOT = Path.home() / "consensus-project"
MEM  = ROOT / "memory" / "logs"
TODAY = date.today().isoformat()

def iso_now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def read_lines(p: Path, default=""):
    try: return p.read_text(encoding="utf-8").splitlines()
    except Exception: return default.splitlines()

def last_git_commit():
    try:
        out = subprocess.check_output(
            ["git","log","-1","--pretty=%H %cI %s"], cwd=ROOT, text=True
        ).strip()
        return out
    except Exception:
        return ""
