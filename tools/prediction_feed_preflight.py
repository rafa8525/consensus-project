#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path

CRIT = "CRITICAL"
WARN = "WARN"
OK = "OK"


@dataclass
class Check:
    level: str
    msg: str


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def newest_mtime(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda p: p.stat().st_mtime)


def find_recent_files(root: Path, patterns: list[str], days: int = 2) -> list[Path]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    out: list[Path] = []
    for pat in patterns:
        for s in glob.glob(str(root / pat), recursive=True):
            p = Path(s)
            try:
                if not p.is_file():
                    continue
                mt = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
                if mt >= cutoff:
                    out.append(p)
            except FileNotFoundError:
                # race: file deleted between glob and stat
                pass
    return out


def safe_size(p: Path) -> int:
    try:
        return p.stat().st_size
    except FileNotFoundError:
        return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path.home() / "consensus-project"))
    ap.add_argument("--mem-root", default=str(Path.home() / "memory"))
    ap.add_argument("--days", type=int, default=2, help="how many days back counts as 'recent'")
    ap.add_argument("--strict", action="store_true", help="exit nonzero on WARN too")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    mem = Path(args.mem_root).expanduser().resolve()

    checks: list[Check] = []

    # Core paths
    if not repo.exists():
        checks.append(Check(CRIT, f"Repo path missing: {repo}"))
    else:
        checks.append(Check(OK, f"Repo path OK: {repo}"))

    if not mem.exists():
        checks.append(Check(CRIT, f"Memory root missing: {mem}"))
    else:
        checks.append(Check(OK, f"Memory root OK: {mem}"))

    # Prediction output dirs (canonical)
    pred_dir = mem / "logs/system/predictions"
    try:
        pred_dir.mkdir(parents=True, exist_ok=True)
        checks.append(Check(OK, f"Predictions dir OK (create-if-missing): {pred_dir}"))
    except Exception as e:
        checks.append(Check(CRIT, f"Cannot ensure predictions dir: {pred_dir} ({e})"))

    # System health snapshot
    shs = mem / "logs/status/system_health_snapshot.md"
    if shs.is_file():
        checks.append(Check(OK, f"System health snapshot found: {shs} ({safe_size(shs)} bytes)"))
    else:
        checks.append(Check(WARN, f"System health snapshot missing: {shs}"))

    # Fitness signals:
    # - "true" fitness logs in logs/fitness
    # - plus the newer audit outputs living in logs/system
    fitness_patterns = [
        "logs/fitness/**/*.md",
        "logs/fitness/**/*.csv",
        "logs/fitness/**/*steps*.*",
        "logs/fitness/**/*swim*.*",
        "logs/fitness/**/*fitbit*.*",
        "logs/system/fitness_audit_summary.md",
        "logs/system/fitness_audit.log",
    ]
    recent_fitness = find_recent_files(mem, fitness_patterns, days=args.days)
    if recent_fitness:
        newest = newest_mtime(recent_fitness)
        checks.append(Check(OK, f"Recent fitness signal(s) found: {len(recent_fitness)}; newest={newest}"))
    else:
        checks.append(
            Check(
                WARN,
                f"No fitness signals in last {args.days} day(s) under {mem}/logs "
                f"(patterns checked: {len(fitness_patterns)})",
            )
        )

    # Movie export sanity
    movie_export = mem / "exports/movie_list_export.txt"
    if movie_export.is_file():
        sz = safe_size(movie_export)
        if sz < 300:  # small often indicates a stub export
            checks.append(Check(WARN, f"Movie export looks tiny ({sz} bytes): {movie_export}"))
        else:
            checks.append(Check(OK, f"Movie export OK ({sz} bytes): {movie_export}"))
    else:
        checks.append(Check(WARN, f"Movie export missing: {movie_export}"))

    # Repo mirror sanity (optional)
    mirror = repo / "memory/logs/system/predictions"
    if mirror.exists():
        checks.append(Check(OK, f"Repo mirror predictions dir exists: {mirror}"))
    else:
        checks.append(Check(WARN, f"Repo mirror predictions dir missing (agent may create it): {mirror}"))

    # Print report
    print(f"[preflight] {iso_now()} repo={repo} mem_root={mem} days={args.days}")

    worst = OK
    for c in checks:
        print(f"- [{c.level}] {c.msg}")
        if c.level == CRIT:
            worst = CRIT
        elif c.level == WARN and worst != CRIT:
            worst = WARN

    if worst == CRIT:
        return 2
    if worst == WARN and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
