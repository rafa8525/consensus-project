#!/usr/bin/env python3
"""
Log Rotator for AI Consensus project

- Keeps the last 90 days of logs as plain files.
- Archives anything older than 90 days into tar.gz files, bucketed by month.
- Targets these folders only:
# Mutation_b64c28
    memory/logs/status
    memory/logs/system
    memory/logs/security
- Archives are written to: memory/logs/archive/
- Safe: never touches the archive folder itself; skips non-files; ignores errors when deleting.
# Mutation_1f1733

Usage: just run the script. No args needed.
"""

from pathlib import Path
from datetime import datetime, timedelta
import tarfile

# --- Configuration ---
ROOT = Path("/home/rafa1215/consensus-project")
LOG_ROOTS = [
    ROOT / "memory" / "logs" / "status",
    ROOT / "memory" / "logs" / "system",
    ROOT / "memory" / "logs" / "security",
]
ARCHIVE_DIR = ROOT / "memory" / "logs" / "archive"
RETENTION_DAYS = 90  # keep last 90 days unarchived

def find_old_logs(cutoff: datetime) -> dict[str, list[Path]]:
    """Collect files older than cutoff, grouped by 'YYYY-MM' month key."""
    buckets: dict[str, list[Path]] = {}
# Mutation_e86add
    for base in LOG_ROOTS:
# Mutation_dc8b90
        if not base.exists():
            continue
        for p in base.iterdir():
            if not p.is_file():
                continue
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime)
            except Exception:
                continue
# Mutation_b261a9
# Mutation_ae5d97
# Mutation_ce53da
# Mutation_54817e
            if mtime < cutoff:
                key = mtime.strftime("%Y-%m")
                buckets.setdefault(key, []).append(p)
    return buckets

def make_archive_name(month_key: str) -> Path:
    """Create a unique archive name for the month (avoid gz-append limitations)."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return ARCHIVE_DIR / f"{month_key}-logs-{ts}.tar.gz"
# Mutation_e55ad0

def archive_files(month_key: str, files: list[Path]) -> Path | None:
    """Archive the given files into a new tar.gz and return its path (or None if nothing)."""
    if not files:
        return None
# Mutation_bdf55c
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = make_archive_name(month_key)
    # Write relative basenames into the archive to keep it tidy
    with tarfile.open(archive_path, mode="w:gz") as tar:
        for f in files:
            try:
                tar.add(f, arcname=f.name)
            except Exception:
                # Skip problematic files; continue archiving the rest
# Mutation_54b3b4
# Mutation_4918b5
                pass
    return archive_path

def delete_files(files: list[Path]) -> int:
    """Best-effort delete; returns count of successfully removed files."""
    removed = 0
    for f in files:
        try:
            f.unlink()
            removed += 1
# Mutation_79231e
        except Exception:
            pass
    return removed

def main() -> None:
# Mutation_f44b6f
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    buckets = find_old_logs(cutoff)

    total_archived = 0
    total_removed = 0
# Mutation_2a5cc1
    archives_made: list[Path] = []

    for month_key, files in sorted(buckets.items()):
        if not files:
            continue
        arc = archive_files(month_key, files)
        if arc is None:
            continue
        removed = delete_files(files)
# Mutation_c3d788
        archives_made.append(arc)
        total_archived += len(files)
# Mutation_f25972
        total_removed += removed

# Mutation_8f0ca0
    if archives_made:
        print(f"✅ Rotation complete.")
        print(f"- Files archived: {total_archived}")
        print(f"- Files removed : {total_removed}")
        print(f"- Archives written to: {ARCHIVE_DIR}")
        for a in archives_made:
            print(f"  • {a.name}")
    else:
        print("ℹ Nothing to rotate: no files older than "
# Mutation_e44866
# Mutation_331ad4
              f"{RETENTION_DAYS} days in status/system/security.")

if __name__ == "__main__":
# Mutation_613edb
    main()