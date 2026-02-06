#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_DIR = Path("/home/rafa1215/consensus-project")
PUBLIC_DIR = REPO_DIR / "memory" / "public"
OUT_JSON = PUBLIC_DIR / "absorption_last_success.json"

LOCAL_LOG = REPO_DIR / "memory" / "logs" / "system" / "absorption_timestamp.log"

def sh(*args: str) -> str:
    return subprocess.check_output(args, cwd=str(REPO_DIR), text=True).strip()

def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)  # atomic on same filesystem

def main() -> int:
    now_utc = datetime.now(timezone.utc)
    ts_utc = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    # best-effort git metadata
    try:
        commit = sh("git", "rev-parse", "--short", "HEAD")
    except Exception:
        commit = None

    payload = {
        "ts_utc": ts_utc,
        "status": "ok",
        "git_commit": commit,
        "source": "post-absorption hook",
    }

    atomic_write_json(OUT_JSON, payload)

    # keep your local log updated too (append or overwrite—here overwrite for simplicity)
    LOCAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    tmp = LOCAL_LOG.with_suffix(".log.tmp")
    line = f"{ts_utc} OK public_marker_written\n"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOCAL_LOG)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
