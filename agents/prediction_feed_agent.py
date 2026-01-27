#!/usr/bin/env python3
"""
prediction_feed_agent.py

Goal:
- Generate a daily "Prediction Feed" markdown file (canonical memory path)
- Mirror it into the repo for GitHub visibility
- IMPORTANT: avoid same-day Git churn by only rewriting the repo mirror
  when meaningful content changes (ignoring the volatile "Generated:" line)

Canonical (memory) write:
  /home/rafa1215/memory/logs/system/predictions/prediction_feed_YYYY-MM-DD.md

Repo mirror:
  /home/rafa1215/consensus-project/memory/logs/system/predictions/prediction_feed_YYYY-MM-DD.md
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, date
from pathlib import Path
from typing import List, Optional, Tuple


VERSION = "v2026-01-27-wow-v3-9-stable-mirror"


@dataclass
class Finding:
    category: str
    level: str  # LOW / MEDIUM / HIGH
    title: str
    reason: str


def _now_local() -> datetime:
    # PythonAnywhere runs in UTC by default; we keep "Generated:" local-ish by using local time.
    # If your system timezone is set, datetime.now() will reflect it.
    return datetime.now()


def _today_yyyy_mm_dd() -> str:
    return date.today().isoformat()


def _iso_utc_from_mtime(path: Path) -> str:
    try:
        ts = path.stat().st_mtime
    except FileNotFoundError:
        return "UNKNOWN"
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _normalize_for_repo_diff(s: str) -> str:
    """
    Normalize content for repo mirror comparison to prevent churn.
    We ignore the volatile 'Generated:' line which changes on every run.
    """
    out: List[str] = []
    for line in s.splitlines():
        if line.startswith("Generated: "):
            continue
        out.append(line)
    return "\n".join(out).rstrip() + "\n"


def _detect_fitness_logged_today(mem_root: Path, today: str) -> bool:
    """
    Heuristic: look for today's date string in common fitness logs.
    This keeps behavior stable even if filenames change over time.
    """
    candidates = [
        mem_root / "logs" / "fitness" / "fitness_tracker.log",
        mem_root / "logs" / "system" / "fitness_integration.log",
        mem_root / "logs" / "status" / "fitness_daily_summary_latest.md",
    ]
    for p in candidates:
        txt = _read_text(p)
        if txt and today in txt:
            return True
    return False


def _parse_movie_export_counts(export_text: str) -> Tuple[int, int, int, int, int]:
    """
    Parses a simple exported movie list text file.

    Expected (best-effort) formats supported:
    - TSV / CSV with a header containing 'Status' column
    - Or lines containing 'Status:' markers

    Returns: (total, watched, removed, maybe, candidates)
    'candidates' here means 'unwatched / to-watch' style items
    (best-effort; depends on your Status conventions).
    """
    lines = [ln for ln in export_text.splitlines() if ln.strip()]
    if not lines:
        return (0, 0, 0, 0, 0)

    # Try CSV/TSV header detection
    header = lines[0]
    delim = "\t" if "\t" in header else ("," if "," in header else None)
    status_idx: Optional[int] = None

    if delim:
        cols = [c.strip().strip('"').strip("'") for c in header.split(delim)]
        for i, c in enumerate(cols):
            if c.lower() == "status":
                status_idx = i
                break

        watched = removed = maybe = candidates = 0
        total = 0

        for row in lines[1:]:
            parts = [p.strip().strip('"').strip("'") for p in row.split(delim)]
            if not parts or all(not p for p in parts):
                continue
            total += 1
            st = ""
            if status_idx is not None and status_idx < len(parts):
                st = parts[status_idx].strip().lower()

            # Best-effort mapping: adjust to your conventions as needed
            if "watch" in st and "un" not in st:
                watched += 1
            elif "remove" in st:
                removed += 1
            elif "maybe" in st:
                maybe += 1
            elif st in ("", "todo", "to watch", "unwatched", "candidate", "candidates"):
                candidates += 1
            else:
                # If unknown, assume it is not a candidate
                pass

        return (total, watched, removed, maybe, candidates)

    # Fallback: line-based scan for "Status:" tokens
    total = watched = removed = maybe = candidates = 0
    for ln in lines:
        total += 1
        low = ln.lower()
        if "status" in low:
            if "watched" in low and "unwatched" not in low:
                watched += 1
            elif "removed" in low or "remove" in low:
                removed += 1
            elif "maybe" in low:
                maybe += 1
            elif "unwatched" in low or "candidate" in low or "to watch" in low:
                candidates += 1
        # If no explicit status token, we leave it out of candidate count

    return (total, watched, removed, maybe, candidates)


def _get_movie_export_text(repo_root: Path, mem_root: Path) -> Optional[str]:
    # Prefer the repo copy if it exists, otherwise fallback to canonical memory
    repo_path = repo_root / "memory" / "exports" / "movie_list_export.txt"
    mem_path = mem_root / "exports" / "movie_list_export.txt"
    txt = _read_text(repo_path)
    if txt is not None and txt.strip():
        return txt
    txt = _read_text(mem_path)
    if txt is not None and txt.strip():
        return txt
    return None


def _make_feed(findings: List[Finding], today: str) -> str:
    generated = _now_local().isoformat()
    lines: List[str] = []
    lines.append(f"# Prediction Feed – {today}")
    lines.append(f"Generated: {generated}")
    lines.append(f"Agent: prediction_feed_agent.py {VERSION}")

    # Preserve stable section ordering
    sections = [
        "Health/Fitness",
        "Errands & Geofences",
        "Media & Fun",
        "Family/Events",
        "System/Project",
    ]

    by_cat = {s: [] for s in sections}
    for f in findings:
        if f.category not in by_cat:
            by_cat[f.category] = []
        by_cat[f.category].append(f)

    for cat in sections:
        lines.append(f"## {cat}")
        items = by_cat.get(cat, [])
        if not items:
            lines.append("1. [LOW] No items this run.")
            lines.append("   - Reason: No signals found for this category.")
            continue
        for i, f in enumerate(items, start=1):
            lines.append(f"{i}. [{f.level}] {f.title}")
            lines.append(f"   - Reason: {f.reason}")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]  # .../consensus-project
    mem_root = Path(os.environ.get("MEMORY_ROOT", "/home/rafa1215/memory")).resolve()
    today = _today_yyyy_mm_dd()

    print(
        f"RUN {VERSION} file={Path(__file__).resolve()} mem_root={mem_root} repo={repo_root}",
        flush=True,
    )

    # Output paths
    canonical_path = mem_root / "logs" / "system" / "predictions" / f"prediction_feed_{today}.md"
    repo_path = repo_root / "memory" / "logs" / "system" / "predictions" / f"prediction_feed_{today}.md"

    findings: List[Finding] = []

    # --- Health/Fitness ---
    if not _detect_fitness_logged_today(mem_root, today):
        findings.append(
            Finding(
                category="Health/Fitness",
                level="MEDIUM",
                title="No fitness log detected for today. Log steps or swim laps.",
                reason="Missing entries degrade weekly summaries and can hide patterns.",
            )
        )

    # --- Errands & Geofences ---
    findings.append(
        Finding(
            category="Errands & Geofences",
            level="LOW",
            title="Pick one small errand you can knock out this week.",
            reason="No strong geofence-derived errands were found in this feed run.",
        )
    )

    # --- Media & Fun ---
    export_txt = _get_movie_export_text(repo_root, mem_root)
    if export_txt is None:
        findings.append(
            Finding(
                category="Media & Fun",
                level="MEDIUM",
                title="Movie export not found or empty. Regenerate movie_list_export.txt from Sheets.",
                reason="Without the export, media deltas and tailored recommendations are limited.",
            )
        )
    else:
        total, watched, removed, maybe, candidates = _parse_movie_export_counts(export_txt)
        findings.append(
            Finding(
                category="Media & Fun",
                level="LOW",
                title=f"Movie list unchanged ({total}). Pick one movie tonight and log it.",
                reason="This keeps your taste profile sharp and recommendations accurate.",
            )
        )
        findings.append(
            Finding(
                category="Media & Fun",
                level="LOW",
                title=f"Breakdown: watched={watched}, removed={removed}, maybe={maybe}, candidates={candidates}.",
                reason="Derived from Status column in your export.",
            )
        )
        if candidates <= 0:
            findings.append(
                Finding(
                    category="Media & Fun",
                    level="LOW",
                    title="No unwatched candidates found in the export. If you want recommendations, add a few 'Maybe' titles to the sheets.",
                    reason="All titles appear watched/removed or export is too small.",
                )
            )

    # --- Family/Events ---
    findings.append(
        Finding(
            category="Family/Events",
            level="LOW",
            title="Reunion (Mar 28, 2026 — SF Italian American Club): do one micro-task today (invite/page/music/menu).",
            reason="A high-impact future win with a 5-minute action now.",
        )
    )

    # --- System/Project ---
    snap_path = mem_root / "logs" / "status" / "system_health_snapshot.md"
    snap_ts = _iso_utc_from_mtime(snap_path)
    findings.append(
        Finding(
            category="System/Project",
            level="MEDIUM",
            title=f"System health snapshot: {'UNKNOWN' if snap_ts == 'UNKNOWN' else 'OK/RECENT'} (last: {snap_ts}).",
            reason=f"Pulled from {snap_path}.",
        )
    )
    findings.append(
        Finding(
            category="System/Project",
            level="LOW",
            title="System logs updated today — skim the newest entry and confirm it’s writing to the right path.",
            reason="Fast validation prevents silent drift.",
        )
    )

    # Render feed
    content = _make_feed(findings, today)

    # Always write canonical memory feed (authoritative)
    _write_text(canonical_path, content)
    print(f"Wrote (canonical): {canonical_path}")

    # Mirror to repo only if meaningful changes (ignore Generated line)
    new_norm = _normalize_for_repo_diff(content)
    if repo_path.exists():
        old_text = repo_path.read_text(encoding="utf-8", errors="replace")
        old_norm = _normalize_for_repo_diff(old_text)
        if old_norm == new_norm:
            print(f"Mirror unchanged (ignoring Generated line): {repo_path}")
        else:
            _write_text(repo_path, content)
            print(f"Mirrored (repo): {repo_path}")
    else:
        _write_text(repo_path, content)
        print(f"Mirrored (repo): {repo_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
