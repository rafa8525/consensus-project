#!/usr/bin/env python3
"""Read-only validation of authoritative ACS-02 absorption evidence.

No legacy log-size heuristics. Never claims cross-agent knowledge consumption,
only verified freshness and structure of the established absorption output.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home()
MARKER = ROOT / "memory/public/absorption_last_success.json"
KB = ROOT / "consensus-project/memory/centralized_knowledge_base.txt"
MAX_AGE_HOURS = 36

def evaluate(marker: Path = MARKER, kb: Path = KB,
             now: datetime | None = None) -> tuple[bool, str]:
    now = datetime.now(timezone.utc) if now is None else now
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
        if payload.get("status") != "ok":
            return False, "ACS-02 absorption marker is not OK"
        raw_stamp = str(payload["last_success_utc"])
        stamp = datetime.fromisoformat(raw_stamp.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            return False, "ACS-02 marker timestamp lacks timezone"
        age = (now - stamp.astimezone(timezone.utc)).total_seconds() / 3600
        if not -5/60 <= age <= MAX_AGE_HOURS:
            return False, "ACS-02 absorption marker is stale/future dated"
        with kb.open("r", encoding="utf-8") as f:
            header = [f.readline().strip() for _ in range(3)]
        if header[0] != "Centralized Knowledge Base" or not header[2].startswith("Generated (UTC): "):
            return False, "ACS-02 knowledge base structure invalid"
        if kb.stat().st_size <= 0:
            return False, "ACS-02 knowledge base empty"
        if payload.get("centralized_knowledge_base_size_bytes") != kb.stat().st_size:
            return False, "ACS-02 marker does not describe current knowledge base"
        return True, "Verified canonical ACS-02 absorption evidence"
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError):
        return False, "Missing or invalid ACS-02 knowledge evidence"

def run() -> int:
    ok, detail = evaluate()
    print(("PASS" if ok else "FAIL") + " knowledge_sharing_validator: " + detail)
    return 0 if ok else 1

def main() -> int:
    return run()

if __name__ == "__main__":
    raise SystemExit(main())
