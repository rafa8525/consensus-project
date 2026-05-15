#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LOCAL_TZ = "America/Los_Angeles"

REPO_ROOT = Path("/home/rafa1215/consensus-project")
MEM_ROOT = Path("/home/rafa1215/memory")
REPO_EXPORT = REPO_ROOT / "memory" / "exports" / "movie_list_export.txt"
CANON_EXPORT = MEM_ROOT / "exports" / "movie_list_export.txt"
PUBLIC_DIR = MEM_ROOT / "public"
MARKER_PATH = PUBLIC_DIR / "absorption_last_success.json"
CKB_PATH = REPO_ROOT / "memory" / "centralized_knowledge_base.txt"


def utc_now():
    return datetime.now(tz=ZoneInfo("UTC"))


def local_now():
    return datetime.now(tz=ZoneInfo(LOCAL_TZ))


def iso_utc_z(dt: datetime) -> str:
    return dt.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(REPO_ROOT),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return out or "unknown"
    except Exception:
        return "unknown"


def choose_export_path() -> Path:
    if CANON_EXPORT.exists():
        return CANON_EXPORT
    return REPO_EXPORT


def main() -> int:
    export_path = choose_export_path()

    if not export_path.exists():
        print(f"ERROR: export file not found: {export_path}", file=sys.stderr)
        return 1

    export_stat = export_path.stat()

    ckb_size = None
    if CKB_PATH.exists():
        try:
            ckb_size = CKB_PATH.stat().st_size
        except Exception:
            ckb_size = None

    now_utc = utc_now()
    now_local = local_now()

    payload = {
        "last_success_local": now_local.isoformat(),
        "last_success_utc": now_utc.isoformat(),
        "local_tz": LOCAL_TZ,
        "status": "ok",
        "export_size_bytes": export_stat.st_size,
        "export_mtime_utc": export_stat.st_mtime,
        "export_mtime_iso_utc": iso_utc_z(datetime.fromtimestamp(export_stat.st_mtime, tz=ZoneInfo("UTC"))),
        "source": "absorption public marker",
        "git_commit": get_git_commit(),
        "marker_write_iso_utc": iso_utc_z(now_utc),
    }

    if ckb_size is not None:
        payload["centralized_knowledge_base_size_bytes"] = ckb_size

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = MARKER_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp_path, MARKER_PATH)

    print(f"WROTE: {MARKER_PATH}")
    print(f"last_success_local={payload['last_success_local']}")
    print(f"git_commit={payload['git_commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())