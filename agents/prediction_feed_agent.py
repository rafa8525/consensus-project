#!/usr/bin/env python3
"""
prediction_feed_agent.py

Generates a daily "Prediction Feed" markdown file in canonical memory storage:
  /home/rafa1215/memory/logs/system/predictions/prediction_feed_YYYY-MM-DD.md

And mirrors it into the repo:
  /home/rafa1215/consensus-project/memory/logs/system/predictions/prediction_feed_YYYY-MM-DD.md

Mirror update is skipped if the only difference is the "Generated:" line.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


VERSION = "v2026-01-28-wow-v4-0-audit-signal"


# ----------------------------
# Utilities
# ----------------------------

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def today_ymd() -> str:
    return utc_now().date().isoformat()


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="microseconds")


def safe_read_text(p: Path, max_bytes: int = 1_000_000) -> str:
    try:
        data = p.read_bytes()
        if len(data) > max_bytes:
            data = data[:max_bytes]
        return data.decode("utf-8", errors="replace")
    except FileNotFoundError:
        return ""
    except Exception:
        return ""


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def normalize_for_compare(md_text: str) -> str:
    """
    Compare documents while ignoring the dynamic Generated line.
    """
    out_lines = []
    for line in md_text.splitlines():
        if line.startswith("Generated:"):
            continue
        out_lines.append(line)
    return "\n".join(out_lines).rstrip() + "\n"


def write_text_atomic(path: Path, text: str) -> None:
    """
    Atomic write: write to temp file in same directory then replace.
    """
    ensure_dir(path.parent)
    tmp = path.with_name(f".{path.name}.tmp")
    data = text.encode("utf-8")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def list_recent_files(root: Path, patterns: Iterable[str], since_dt: datetime) -> list[Path]:
    """
    Return files matching patterns (glob relative to root) whose mtime >= since_dt.
    """
    out: list[Path] = []
    since_ts = since_dt.timestamp()
    for pat in patterns:
        for p in root.glob(pat):
            try:
                if p.is_file() and p.stat().st_mtime >= since_ts:
                    out.append(p)
            except FileNotFoundError:
                continue
    return out


def file_mtime_dt(p: Path) -> datetime | None:
    try:
        return datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
    except FileNotFoundError:
        return None


# ----------------------------
# Parsers
# ----------------------------

ISO_TS_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\b")


def parse_last_iso_timestamp(text: str) -> str | None:
    """
    Find the last ISO-ish timestamp in a text blob.
    """
    matches = ISO_TS_RE.findall(text)
    if not matches:
        return None
    return matches[-1]


@dataclass
class MovieCounts:
    total: int
    watched: int
    removed: int
    maybe: int
    candidates: int
    unknown: int


def _split_row(line: str) -> list[str]:
    """
    Heuristic splitter for unknown export format:
    - prefer tab
    - else pipe
    - else comma
    """
    if "\t" in line:
        return [c.strip() for c in line.split("\t")]
    if "|" in line:
        return [c.strip() for c in line.split("|")]
    if "," in line:
        return [c.strip() for c in line.split(",")]
    # fallback: multiple spaces
    return [c.strip() for c in re.split(r"\s{2,}", line.strip()) if c.strip()]


def _norm_status(s: str) -> str:
    x = s.strip().lower()
    x = re.sub(r"\s+", " ", x)
    return x


def parse_movie_export(export_path: Path) -> tuple[MovieCounts, list[tuple[str, str]]]:
    """
    Returns:
      (counts, rows)
    rows: list of (title, status_norm)
    """
    text = safe_read_text(export_path, max_bytes=3_000_000)
    lines = [ln.strip("\n\r") for ln in text.splitlines() if ln.strip()]
    if not lines:
        return MovieCounts(0, 0, 0, 0, 0, 0), []

    # Detect header row if present.
    header = _split_row(lines[0])
    title_idx = 0
    status_idx = 1 if len(header) > 1 else 0

    header_norm = [_norm_status(h) for h in header]
    if any("movie" in h and "title" in h for h in header_norm) or any(h == "title" for h in header_norm):
        # likely a header
        # try to locate "title" and "status"
        for i, h in enumerate(header_norm):
            if "title" in h:
                title_idx = i
            if "status" in h:
                status_idx = i
        data_lines = lines[1:]
    else:
        data_lines = lines

    rows: list[tuple[str, str]] = []
    for ln in data_lines:
        cols = _split_row(ln)
        if not cols:
            continue
        if title_idx >= len(cols):
            # cannot parse
            continue
        title = cols[title_idx].strip()
        if not title or title.lower() in ("movie title", "title"):
            continue
        status = ""
        if status_idx < len(cols):
            status = cols[status_idx].strip()
        rows.append((title, _norm_status(status)))

    # Deduplicate by title while keeping "best" status if multiple lines.
    # Priority: watched/removed/maybe/candidate/unknown
    pri = {"watched": 5, "removed": 4, "maybe": 3, "candidate": 2, "unwatched": 2, "": 0}
    best: dict[str, str] = {}
    for title, st in rows:
        key = title.strip()
        if key not in best:
            best[key] = st
            continue
        a = best[key]
        if pri.get(st, 1) > pri.get(a, 1):
            best[key] = st

    # Count categories
    watched = removed = maybe = candidates = unknown = 0
    normalized_rows: list[tuple[str, str]] = []
    for title, st in best.items():
        stn = _norm_status(st)
        normalized_rows.append((title, stn))

        if not stn:
            unknown += 1
        elif "watch" in stn and "unwatch" not in stn:
            watched += 1
        elif "remove" in stn or stn in ("rm", "deleted"):
            removed += 1
        elif "maybe" in stn:
            maybe += 1
        elif "candidate" in stn or "unwatched" in stn or stn in ("to watch", "towatch", "todo", "queue"):
            candidates += 1
        else:
            # treat other statuses as unknown
            unknown += 1

    total = len(best)
    return MovieCounts(total, watched, removed, maybe, candidates, unknown), normalized_rows


# ----------------------------
# Fitness detection
# ----------------------------

def fitness_audit_note(mem_root: Path) -> str:
    """
    If the fitness audit ran today, return a short note with timestamp.
    This indicates the pipeline ran, not that the user logged activity.
    """
    candidates = [
        mem_root / "logs/system/fitness_audit_summary.md",
        mem_root / "logs/system/fitness_audit.log",
    ]
    today = utc_now().date()
    for p in candidates:
        mt = file_mtime_dt(p)
        if mt and mt.date() == today:
            ts = mt.isoformat(timespec="minutes")
            return f"Fitness audit ran today ({p.name} @ {ts}Z); pipeline OK, but no activity entry was found."
    return ""


def has_activity_log_today(mem_root: Path) -> bool:
    """
    Treat any file under logs/fitness modified today as an activity log.
    (Conservative: won't count audit logs as activity.)
    """
    start_of_today = datetime.combine(utc_now().date(), datetime.min.time(), tzinfo=timezone.utc)
    patterns = [
        "logs/fitness/**/*.md",
        "logs/fitness/**/*.csv",
        "logs/fitness/**/*.log",
    ]
    recent = list_recent_files(mem_root, patterns, since_dt=start_of_today)
    return len(recent) > 0


# ----------------------------
# State
# ----------------------------

def load_state(state_path: Path) -> dict:
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state_path: Path, state: dict) -> None:
    ensure_dir(state_path.parent)
    tmp = state_path.with_name(f".{state_path.name}.tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, state_path)


# ----------------------------
# Feed generation
# ----------------------------

def build_feed(mem_root: Path, repo_root: Path) -> str:
    ymd = today_ymd()
    generated = iso_utc(utc_now())

    lines: list[str] = []
    lines.append(f"# Prediction Feed – {ymd}")
    lines.append(f"Generated: {generated}")
    lines.append(f"Agent: prediction_feed_agent.py {VERSION}")

    # Health/Fitness
    lines.append("## Health/Fitness")
    if has_activity_log_today(mem_root):
        lines.append("1. [LOW] Fitness activity logged today.")
        lines.append("   - Reason: Activity entries were detected under logs/fitness for today.")
    else:
        lines.append("1. [MEDIUM] No fitness log detected for today. Log steps or swim laps.")
        lines.append("   - Reason: Missing entries degrade weekly summaries and can hide patterns.")
        note = fitness_audit_note(mem_root)
        if note:
            lines.append(f"   - Note: {note}")

    # Errands & Geofences (placeholder until geofence-to-errand signals are wired)
    lines.append("## Errands & Geofences")
    lines.append("1. [LOW] Pick one small errand you can knock out this week.")
    lines.append("   - Reason: No strong geofence-derived errands were found in this feed run.")

    # Media & Fun
    lines.append("## Media & Fun")
    export_path = mem_root / "exports/movie_list_export.txt"
    counts, rows = parse_movie_export(export_path)

    # Track unchanged based on hash + count
    state_path = mem_root / "state/prediction_feed_state.json"
    state = load_state(state_path)
    export_bytes = export_path.read_bytes() if export_path.exists() else b""
    export_hash = sha256_bytes(export_bytes)

    last_hash = state.get("movie_export_hash")
    last_count = state.get("movie_total")

    unchanged = (last_hash == export_hash) and (last_count == counts.total) and (counts.total > 0)

    if counts.total == 0:
        lines.append("1. [LOW] Movie export is empty or unreadable. Re-export your movie sheets.")
        lines.append("   - Reason: No titles could be parsed from the export.")
    else:
        if unchanged:
            lines.append(f"1. [LOW] Movie list unchanged ({counts.total}). Pick one movie tonight and log it.")
        else:
            lines.append(f"1. [LOW] Movie list updated ({counts.total}). Consider logging what you watched most recently.")
        lines.append("   - Reason: This keeps your taste profile sharp and recommendations accurate.")

        lines.append(
            f"2. [LOW] Breakdown: watched={counts.watched}, removed={counts.removed}, maybe={counts.maybe}, candidates={counts.candidates}."
        )
        lines.append("   - Reason: Derived from Status column in your export.")

        # If there are no candidates, encourage adding "Maybe"
        if counts.maybe == 0 and counts.candidates == 0:
            lines.append("3. [LOW] No unwatched candidates found in the export. If you want recommendations, add a few 'Maybe' titles to the sheets.")
            lines.append("   - Reason: All titles appear watched/removed, or the export has no candidate statuses.")
        else:
            # List up to 5 "maybe/candidate" titles to nudge action
            picks: list[str] = []
            for title, st in rows:
                if "maybe" in st or "candidate" in st or "unwatched" in st or st in ("to watch", "towatch", "queue"):
                    picks.append(title)
                if len(picks) >= 5:
                    break
            if picks:
                lines.append("3. [LOW] Unwatched picks from your list: " + "; ".join(picks) + ".")
                lines.append("   - Reason: These are tagged as Maybe/Candidate/Unwatched in your export.")

    # Save state for next run
    state["movie_export_hash"] = export_hash
    state["movie_total"] = counts.total
    state["movie_state_updated_utc"] = iso_utc(utc_now())
    save_state(state_path, state)

    # Family/Events
    lines.append("## Family/Events")
    lines.append("1. [LOW] Reunion (Mar 28, 2026 — SF Italian American Club): do one micro-task today (invite/page/music/menu).")
    lines.append("   - Reason: A high-impact future win with a 5-minute action now.")

    # System/Project
    lines.append("## System/Project")
    shs_path = mem_root / "logs/status/system_health_snapshot.md"
    shs_text = safe_read_text(shs_path)
    last_ts = parse_last_iso_timestamp(shs_text)
    if last_ts:
        lines.append(f"1. [MEDIUM] System health snapshot: OK/RECENT (last: {last_ts}).")
    else:
        # fallback to file mtime
        mt = file_mtime_dt(shs_path)
        mt_s = mt.isoformat(timespec="minutes") + "Z" if mt else "unknown"
        lines.append(f"1. [MEDIUM] System health snapshot: present (mtime: {mt_s}).")
    lines.append(f"   - Reason: Pulled from {shs_path}.")

    lines.append("2. [LOW] System logs updated today — skim the newest entry and confirm it’s writing to the right path.")
    lines.append("   - Reason: Fast validation prevents silent drift.")

    return "\n".join(lines).rstrip() + "\n"


# ----------------------------
# Main
# ----------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mem-root", default=str(Path.home() / "memory"), help="canonical memory root")
    ap.add_argument("--repo", default=str(Path.home() / "consensus-project"), help="repo root for mirror")
    args = ap.parse_args()

    mem_root = Path(args.mem_root).expanduser().resolve()
    repo_root = Path(args.repo).expanduser().resolve()
    agent_file = Path(__file__).resolve()

    print(f"RUN {VERSION} file={agent_file} mem_root={mem_root} repo={repo_root}")

    ymd = today_ymd()
    canonical_path = mem_root / "logs/system/predictions" / f"prediction_feed_{ymd}.md"
    mirror_path = repo_root / "memory/logs/system/predictions" / f"prediction_feed_{ymd}.md"

    feed = build_feed(mem_root=mem_root, repo_root=repo_root)

    # Write canonical always
    write_text_atomic(canonical_path, feed)
    print(f"Wrote (canonical): {canonical_path}")

    # Mirror: only write if content differs beyond Generated line
    existing_mirror = safe_read_text(mirror_path)
    if existing_mirror:
        if normalize_for_compare(existing_mirror) == normalize_for_compare(feed):
            print(f"Mirror unchanged (ignoring Generated line): {mirror_path}")
            return 0

    write_text_atomic(mirror_path, feed)
    print(f"Mirrored (repo): {mirror_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
