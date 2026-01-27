#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

VERSION = "2026-01-26-wow-v3-8-media-deltas"

DEFAULT_MEM_ROOT = "/home/rafa1215/memory"
DEFAULT_REPO_ROOT = "/home/rafa1215/consensus-project"

STATE_PATH_REL = "state/prediction_feed_state.json"
PRED_DIR_REL = "logs/system/predictions"
SYSTEM_HEALTH_SNAPSHOT_REL = "logs/status/system_health_snapshot.md"

MOVIE_EXPORT_CANON_REL = "exports/movie_list_export.txt"
MOVIE_EXPORT_REPO_REL = "memory/exports/movie_list_export.txt"


@dataclass
class Item:
    category: str
    priority: str  # LOW/MEDIUM/HIGH
    text: str
    reason: str


def now_local_iso() -> str:
    return dt.datetime.now().isoformat(timespec="microseconds")


def today_local_date() -> str:
    return dt.date.today().isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(read_text(path))
    except Exception:
        return {}


def save_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()


def clamp_list(xs: Sequence[str], n: int) -> List[str]:
    out: List[str] = []
    for x in xs:
        if x and x not in out:
            out.append(x)
        if len(out) >= n:
            break
    return out


def parse_system_health_snapshot(snapshot_path: Path) -> Tuple[str, str]:
    """
    Returns (overall_status, generated_line_value) where status is OK/WARN/ERROR/UNKNOWN.
    """
    if not snapshot_path.exists():
        return ("UNKNOWN", "missing")
    txt = read_text(snapshot_path)
    overall = "UNKNOWN"
    generated = "unknown"
    for line in txt.splitlines():
        if line.startswith("- Generated:"):
            generated = line.split(":", 1)[1].strip()
        if line.startswith("- OVERALL:"):
            overall = line.split(":", 1)[1].strip().upper()
    if overall not in ("OK", "WARN", "ERROR", "UNKNOWN"):
        overall = "UNKNOWN"
    return (overall, generated)


def detect_any_fitness_log_today(mem_root: Path) -> bool:
    """
    Heuristic: if anything in logs/fitness contains today's date in filename, treat as logged.
    """
    d = mem_root / "logs" / "fitness"
    if not d.exists():
        return False
    today = dt.date.today().isoformat()
    for p in d.glob("*"):
        if p.is_file() and today in p.name:
            return True
    return False


def parse_movie_export(export_path: Path) -> Tuple[List[Tuple[str, str, str, str]], List[str]]:
    """
    Parse lines of format:
      Title<TAB>Year<TAB>Status<TAB>Preference
    (Your file may have spaces; we handle both tab and multi-space.)
    Returns:
      rows: list of (title, year, status, preference)
      problems: list of warnings
    """
    problems: List[str] = []
    if not export_path.exists():
        problems.append(f"missing export at {export_path}")
        return ([], problems)

    rows: List[Tuple[str, str, str, str]] = []
    for raw in read_text(export_path).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        # Prefer tabs; fallback to 2+ spaces as separator
        if "\t" in raw:
            parts = [p.strip() for p in raw.split("\t")]
        else:
            parts = [p.strip() for p in re.split(r"\s{2,}", raw.strip())]

        if len(parts) < 2:
            continue

        # Normalize to 4 fields
        title = parts[0]
        year = parts[1] if len(parts) >= 2 else ""
        status = parts[2] if len(parts) >= 3 else ""
        pref = parts[3] if len(parts) >= 4 else ""

        # Strip any leading numbering like "1." that can appear in titles
        title = re.sub(r"^\s*\d+\.\s*", "", title).strip()

        if not title:
            continue

        rows.append((title, year, status, pref))

    if not rows:
        problems.append("export had no parsable rows (only comments/empty)")
    return (rows, problems)


def status_bucket(status: str) -> str:
    s = status.strip().upper()
    if "YES" in s or "WATCHED" in s:
        return "WATCHED"
    if "REMOVED" in s or ("NO" in s and "REMOVED" in s):
        return "REMOVED"
    if "NO" in s:
        return "NO"
    if "MAYBE" in s:
        return "MAYBE"
    return "OTHER"


def build_media_items(mem_root: Path, state: Dict[str, Any]) -> Tuple[List[Item], Dict[str, Any]]:
    items: List[Item] = []
    new_state: Dict[str, Any] = dict(state)

    export_path = mem_root / MOVIE_EXPORT_CANON_REL
    rows, problems = parse_movie_export(export_path)

    if problems:
        items.append(Item(
            category="Media & Fun",
            priority="HIGH",
            text="Movie export missing or unreadable. Run the exporter and verify the output file exists.",
            reason=f"Problems: {', '.join(problems)}"
        ))
        return (items, new_state)

    # Deduplicate by title (case-insensitive), keep latest seen
    by_key: Dict[str, Tuple[str, str, str, str]] = {}
    for (title, year, status, pref) in rows:
        k = title.strip().lower()
        by_key[k] = (title.strip(), year.strip(), status.strip(), pref.strip())

    titles_sorted = sorted([v[0] for v in by_key.values()], key=lambda x: x.lower())
    movie_count = len(titles_sorted)

    # Title set tracking for deltas
    titles_hash = sha256_str("\n".join([t.lower() for t in titles_sorted]))
    prev_hash = str(state.get("last_movie_titles_hash") or "")
    prev_titles = state.get("last_movie_titles") or []
    if not isinstance(prev_titles, list):
        prev_titles = []

    # Count delta (existing behavior)
    prev_count = state.get("last_movie_count")
    try:
        prev_count_i = int(prev_count) if prev_count is not None else None
    except Exception:
        prev_count_i = None

    changed = (prev_hash != "" and prev_hash != titles_hash)

    if prev_count_i is None:
        items.append(Item(
            category="Media & Fun",
            priority="LOW",
            text=f"Movie list loaded ({movie_count}). Delta tracking initialized.",
            reason=f"Pulled from {export_path}. Next run will detect changes."
        ))
    else:
        if movie_count == prev_count_i and not changed:
            items.append(Item(
                category="Media & Fun",
                priority="LOW",
                text=f"Movie list unchanged ({movie_count}). Pick one movie tonight and log it.",
                reason="This keeps your taste profile sharp and recommendations accurate."
            ))
        else:
            delta = movie_count - prev_count_i
            sign = "+" if delta >= 0 else ""
            # Compute added/removed titles when we have prev_titles
            added: List[str] = []
            removed: List[str] = []
            if prev_titles:
                prev_set = {str(t).strip().lower() for t in prev_titles if str(t).strip()}
                cur_set = {t.strip().lower() for t in titles_sorted}
                added = sorted([t for t in titles_sorted if t.strip().lower() not in prev_set], key=str.lower)
                removed = sorted([t for t in prev_titles if str(t).strip().lower() not in cur_set], key=str.lower)

            msg = f"Movie list changed ({sign}{delta}). Now {movie_count} total."
            if added:
                msg += f" Added: {', '.join(clamp_list(added, 8))}."
            if removed:
                msg += f" Removed: {', '.join(clamp_list(removed, 8))}."
            items.append(Item(
                category="Media & Fun",
                priority="MEDIUM",
                text=msg,
                reason="Change detected by comparing the title set to the previous run."
            ))

    # Basic breakdown
    watched = 0
    removed_cnt = 0
    maybe = 0
    candidates: List[Tuple[str, str, str, str]] = []
    for (_, (title, year, status, pref)) in by_key.items():
        b = status_bucket(status)
        if b == "WATCHED":
            watched += 1
        elif b == "REMOVED":
            removed_cnt += 1
        elif b == "MAYBE":
            maybe += 1
            candidates.append((title, year, status, pref))
        else:
            candidates.append((title, year, status, pref))

    items.append(Item(
        category="Media & Fun",
        priority="LOW",
        text=f"Breakdown: watched={watched}, removed={removed_cnt}, maybe={maybe}, candidates={len(candidates)}.",
        reason="Derived from Status column in your export."
    ))

    # Smarter “next picks” (use candidates if present; otherwise generic based on your vibe)
    if candidates:
        # Prefer candidates that are not removed/no, and have years (newer first)
        def score_row(r: Tuple[str, str, str, str]) -> Tuple[int, int, str]:
            title, year, status, pref = r
            y = 0
            try:
                y = int(re.sub(r"\D", "", year)[:4]) if year else 0
            except Exception:
                y = 0
            sb = status_bucket(status)
            penalty = 0
            if sb in ("REMOVED", "NO"):
                penalty += 1000
            if "YES" in status.upper():
                penalty += 2000
            return (-penalty, y, title.lower())

        candidates_sorted = sorted(candidates, key=score_row, reverse=True)
        picks = candidates_sorted[:3]
        if picks:
            lines = []
            for (t, y, s, p) in picks:
                ydisp = y if y else "?"
                lines.append(f"- {t} ({ydisp})")
            items.append(Item(
                category="Media & Fun",
                priority="LOW",
                text="Next 3 picks from your list:\n" + "\n".join(lines),
                reason="Chosen from non-watched candidates in your export."
            ))
    else:
        items.append(Item(
            category="Media & Fun",
            priority="LOW",
            text="No unwatched candidates found in the export. If you want recommendations, add a few 'Maybe' titles to the sheets.",
            reason="All titles appear watched/removed or export is too small."
        ))

    # Update state for next run
    new_state["last_movie_count"] = movie_count
    new_state["last_movie_titles_hash"] = titles_hash
    # Store a compact list for diffs (limit to 500)
    new_state["last_movie_titles"] = titles_sorted[:500]
    new_state["last_movie_export_mtime"] = export_path.stat().st_mtime if export_path.exists() else None

    return (items, new_state)


def render_markdown(items: List[Item], generated_iso: str) -> str:
    # group by category in stable order
    order = ["Health/Fitness", "Errands & Geofences", "Media & Fun", "Family/Events", "System/Project"]
    grouped: Dict[str, List[Item]] = {}
    for it in items:
        grouped.setdefault(it.category, []).append(it)

    lines: List[str] = []
    lines.append(f"# Prediction Feed – {today_local_date()}")
    lines.append(f"Generated: {generated_iso}")
    lines.append(f"Agent: prediction_feed_agent.py v{VERSION}")
    for cat in order:
        if cat not in grouped:
            continue
        lines.append(f"## {cat}")
        for idx, it in enumerate(grouped[cat], start=1):
            lines.append(f"{idx}. [{it.priority}] {it.text}")
            lines.append(f"   - Reason: {it.reason}")
    lines.append("")
    return "\n".join(lines)


def mirror_file(src: Path, dst: Path) -> Optional[str]:
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(read_text(src), encoding="utf-8")
        return None
    except Exception as e:
        return str(e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mem-root", default=DEFAULT_MEM_ROOT)
    ap.add_argument("--repo-root", default=DEFAULT_REPO_ROOT)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    mem_root = Path(args.mem_root)
    repo_root = Path(args.repo_root)

    generated = now_local_iso()

    # Build items
    items: List[Item] = []

    # Health/Fitness
    if detect_any_fitness_log_today(mem_root):
        items.append(Item(
            category="Health/Fitness",
            priority="LOW",
            text="Fitness log detected for today. Keep the streak alive.",
            reason="Found at least one file in logs/fitness with today's date in the filename."
        ))
    else:
        items.append(Item(
            category="Health/Fitness",
            priority="MEDIUM",
            text="No fitness log detected for today. Log steps or swim laps.",
            reason="Missing entries degrade weekly summaries and can hide patterns."
        ))

    # Errands & Geofences (light touch; your geofence engine is separate)
    items.append(Item(
        category="Errands & Geofences",
        priority="LOW",
        text="Pick one small errand you can knock out this week.",
        reason="No strong geofence-derived errands were found in this feed run."
    ))

    # Media & Fun (with deltas)
    state_path = mem_root / STATE_PATH_REL
    state = load_json(state_path)
    media_items, new_state = build_media_items(mem_root, state)
    items.extend(media_items)

    # Family/Events
    items.append(Item(
        category="Family/Events",
        priority="LOW",
        text="Reunion (Mar 28, 2026 — SF Italian American Club): do one micro-task today (invite/page/music/menu).",
        reason="A high-impact future win with a 5-minute action now."
    ))

    # System/Project
    overall, gen_line = parse_system_health_snapshot(mem_root / SYSTEM_HEALTH_SNAPSHOT_REL)
    items.append(Item(
        category="System/Project",
        priority="LOW" if overall == "OK" else "MEDIUM",
        text=f"System health snapshot: {overall} (last: {gen_line}).",
        reason=f"Pulled from {mem_root / SYSTEM_HEALTH_SNAPSHOT_REL}."
    ))
    items.append(Item(
        category="System/Project",
        priority="LOW",
        text="System logs updated today — skim the newest entry and confirm it’s writing to the right path.",
        reason="Fast validation prevents silent drift."
    ))

    # Write prediction feed
    pred_dir = mem_root / PRED_DIR_REL
    out = pred_dir / f"prediction_feed_{today_local_date()}.md"
    text = render_markdown(items, generated)

    print(f"RUN v{VERSION} file={Path(__file__).resolve()} mem_root={mem_root} repo={repo_root}")

    if not args.dry_run:
        write_text(out, text)

        # Mirror into repo (canonical path mirrored into repo path)
        mirror_out = repo_root / "memory" / "logs" / "system" / "predictions" / out.name
        err = mirror_file(out, mirror_out)
        if err:
            print(f"WARN: mirror failed: {err}")
        else:
            print(f"Wrote (canonical): {out}")
            print(f"Mirrored (repo): {mirror_out}")

        # Persist state
        save_json(state_path, new_state)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
