#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List

DEFAULT_CANONICAL = Path("/home/rafa1215/memory")
DEFAULT_REPO = Path("/home/rafa1215/consensus-project")

TARGETS = [
    "memory/logs/system/predictions",
    "memory/logs/status",
    "memory/logs/system/absorb_memory",
    "memory/logs/fitness",
    "memory/exports",
    "docs/repair_history",
]

STALE_HOURS = 72


@dataclass
class TargetStatus:
    target: str
    canonical_exists: bool
    repo_exists: bool
    canonical_latest_mtime: str | None
    repo_latest_mtime: str | None
    canonical_file_count: int
    repo_file_count: int
    status: str
    note: str


def iso_utc(ts: float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def latest_mtime_and_count(path: Path) -> tuple[float | None, int]:
    if not path.exists():
        return None, 0
    if path.is_file():
        return path.stat().st_mtime, 1

    latest = None
    count = 0
    for root, _, files in os.walk(path):
        for name in files:
            p = Path(root) / name
            try:
                mt = p.stat().st_mtime
            except OSError:
                continue
            count += 1
            if latest is None or mt > latest:
                latest = mt
    return latest, count


def classify(c_mt: float | None, r_mt: float | None, c_exists: bool, r_exists: bool) -> tuple[str, str]:
    now = datetime.now(tz=timezone.utc).timestamp()

    if not c_exists and not r_exists:
        return "missing", "Missing in both canonical memory and repo mirror."
    if c_exists and not r_exists:
        return "missing_repo", "Exists in canonical memory but missing in repo mirror."
    if not c_exists and r_exists:
        return "repo_only", "Exists in repo mirror but missing in canonical memory."

    # both exist
    assert c_mt is not None and r_mt is not None
    lag_hours = max(0.0, (c_mt - r_mt) / 3600.0)
    canonical_age_hours = max(0.0, (now - c_mt) / 3600.0)

    if lag_hours > 1:
        return "lagging_repo", f"Repo mirror lags canonical memory by about {lag_hours:.1f} hours."
    if canonical_age_hours > STALE_HOURS:
        return "stale_both", f"No fresh writes seen in canonical memory for about {canonical_age_hours:.1f} hours."
    return "ok", "Canonical memory and repo mirror both look current."


def audit(canonical_root: Path, repo_root: Path) -> List[TargetStatus]:
    out: List[TargetStatus] = []
    for target in TARGETS:
        c_rel = target
        r_rel = target
        c_path = canonical_root / Path(c_rel).relative_to("memory") if c_rel.startswith("memory/") else canonical_root.parent / c_rel
        r_path = repo_root / r_rel

        c_exists = c_path.exists()
        r_exists = r_path.exists()
        c_mt, c_count = latest_mtime_and_count(c_path)
        r_mt, r_count = latest_mtime_and_count(r_path)
        status, note = classify(c_mt, r_mt, c_exists, r_exists)

        out.append(
            TargetStatus(
                target=target,
                canonical_exists=c_exists,
                repo_exists=r_exists,
                canonical_latest_mtime=iso_utc(c_mt),
                repo_latest_mtime=iso_utc(r_mt),
                canonical_file_count=c_count,
                repo_file_count=r_count,
                status=status,
                note=note,
            )
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical-root", default=str(DEFAULT_CANONICAL))
    ap.add_argument("--repo-root", default=str(DEFAULT_REPO))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results = audit(Path(args.canonical_root), Path(args.repo_root))

    if args.json:
        print(json.dumps([asdict(x) for x in results], indent=2))
        return 0

    print("Repo Write Audit")
    print("================")
    for row in results:
        print(f"\nTarget: {row.target}")
        print(f"  status: {row.status}")
        print(f"  canonical_exists: {row.canonical_exists}")
        print(f"  repo_exists:      {row.repo_exists}")
        print(f"  canonical_files:  {row.canonical_file_count}")
        print(f"  repo_files:       {row.repo_file_count}")
        print(f"  canonical_mtime:  {row.canonical_latest_mtime}")
        print(f"  repo_mtime:       {row.repo_latest_mtime}")
        print(f"  note:             {row.note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())