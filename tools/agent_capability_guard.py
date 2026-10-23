#!/usr/bin/env python3
"""Read-only status verification for ACS-01 self-improvement and evaluation.

The canonical ACS-01 supervisor already produces suggestions and evaluation
artifacts. Do not run the legacy log-overwriting repair loop in parallel.
"""
from __future__ import annotations
import json
import time
from pathlib import Path

STATE = Path.home() / "consensus-project/memory/agents/state.json"
MAX_AGE_SECONDS = 36 * 3600

def evaluate(path: Path = STATE, now: float | None = None) -> tuple[bool, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        age = (time.time() if now is None else now) - float(data["last_supervisor_ts"])
        if not -120 <= age <= MAX_AGE_SECONDS:
            return False, "ACS-01 supervisor evidence missing, stale or future dated"
        results = data["last_supervisor_results"]
        if any(results.get(key, {}).get("ok") is not True
               for key in ("self_improve", "evaluation")):
            return False, "ACS-01 self-improvement or evaluation did not complete"
        if results.get("acs_02", {}).get("ok") is not True:
            return False, "ACS-02 knowledge absorption did not verify successfully"
        return True, "ACS-01 improvement/evaluation and ACS-02 absorption verified"
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, AttributeError):
        return False, "ACS-01 authoritative state missing or invalid"

def run() -> int:
    ok, detail = evaluate()
    print(("PASS" if ok else "FAIL") + " agent_capability_guard: " + detail)
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(run())
