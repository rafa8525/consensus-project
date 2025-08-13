from __future__ import annotations
from pathlib import Path
import json

STATE = Path("memory/agents/state.json")
STATE.parent.mkdir(parents=True, exist_ok=True)
if not STATE.exists(): STATE.write_text("{}", encoding="utf-8")

def load() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save(d: dict) -> None:
    STATE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
