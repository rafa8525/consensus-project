#!/usr/bin/env python3
"""
prediction_feed_agent.py

Generates a daily "Prediction Feed" markdown file in canonical memory storage:
  /home/rafa1215/memory/logs/system/predictions/prediction_feed_YYYY-MM-DD.md

And mirrors it into the repo:
  /home/rafa1215/consensus-project/memory/logs/system/predictions/prediction_feed_YYYY-MM-DD.md

Mirror update is skipped if the only difference is the "Generated:" line.

New in v4.2:
- If your movie export has no Maybe/Candidate entries, generates a deterministic
  offline fallback list of 3 recommendations (with IMDb ratings) and logs them to:
    /home/rafa1215/memory/logs/system/predictions/reco_suggestions_YYYY-MM-DD.md
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

VERSION = "v2026-01-28-wow-v4-2-reco-fallback"


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
    matches = ISO_TS_RE.findall(text)
    return matches[-1] if matches else None


@dataclass
class MovieCounts:
    total: int
    watched: int
    removed: int
    maybe: int
    candidates: int
    unknown: int


RANK_PREFIX_RE = re.compile(r"^\s*\d+\.\s*")


def _norm(s: str) -> str:
    x = s.strip().lower()
    x = re.sub(r"\s+", " ", x)
    return x


def parse_movie_export(export_path: Path) -> tuple[MovieCounts, list[tuple[str, str]]]:
    """
    Parse the canonical export format:

    - Header/comment lines start with '#'
    - Data lines are TAB-separated:
        Title<TAB>Year<TAB>Status<TAB>Preference
    - Title often begins with 'N. ' ranking prefix
    - Status values look like:
        'YES (Watched)'
        'NO (Removed)'
        'MAYBE'
        'CANDIDATE'
    """
    text = safe_read_text(export_path, max_bytes=3_000_000)
    raw_lines = [ln.rstrip("\n\r") for ln in text.splitlines()]

    lines = [ln for ln in raw_lines if ln.strip() and not ln.lstrip().startswith("#")]
    if not lines:
        return MovieCounts(0, 0, 0, 0, 0, 0), []

    rows: list[tuple[str, str]] = []
    for ln in lines:
        parts = ln.split("\t")
        if len(parts) < 3:
            parts = re.split(r"\s{2,}", ln.strip())
        if len(parts) < 3:
            continue

        title = parts[0].strip()
        status = parts[2].strip() if len(parts) > 2 else ""

        title = RANK_PREFIX_RE.sub("", title).strip()
        if not title:
            continue

        rows.append((title, _norm(status)))

    pri = {"watched": 4, "removed": 3, "maybe": 2, "candidate": 2, "unknown": 1}

    def classify(stn: str) -> str:
        s = stn
        if "watched" in s or s.startswith("yes"):
            return "watched"
        if "removed" in s or s.startswith("no"):
            return "removed"
        if "maybe" in s:
            return "maybe"
        if "candidate" in s or "unwatched" in s or "to watch" in s or "queue" in s:
            return "candidate"
        return "unknown"

    best: dict[str, str] = {}
    best_class: dict[str, str] = {}
    for title, stn in rows:
        c = classify(stn)
        if title not in best:
            best[title] = stn
            best_class[title] = c
        else:
            if pri.get(c, 1) > pri.get(best_class[title], 1):
                best[title] = stn
                best_class[title] = c

    watched = removed = maybe = candidates = unknown = 0
    normalized_rows: list[tuple[str, str]] = []
    for title, stn in best.items():
        cls = classify(stn)
        normalized_rows.append((title, stn))
        if cls == "watched":
            watched += 1
        elif cls == "removed":
            removed += 1
        elif cls == "maybe":
            maybe += 1
        elif cls == "candidate":
            candidates += 1
        else:
            unknown += 1

    total = len(best)
    return MovieCounts(total, watched, removed, maybe, candidates, unknown), normalized_rows


# ----------------------------
# Fitness detection
# ----------------------------

def fitness_audit_note(mem_root: Path) -> str:
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
    start_of_today = datetime.combine(utc_now().date(), datetime.min.time(), tzinfo=timezone.utc)
    patterns = [
        "logs/fitness/**/*.md",
        "logs/fitness/**/*.csv",
        "logs/fitness/**/*.log",
    ]
    recent = list_recent_files(mem_root, patterns, since_dt=start_of_today)
    return len(recent) > 0


# ----------------------------
# Reco fallback (offline, deterministic)
# ----------------------------

def fallback_recos() -> list[dict]:
    """
    Offline deterministic fallback list for nights when there are no 'Maybe/Candidate' items
    in the export. Keep it stable; update occasionally.
    """
    return [
        {
            "title": "Constantine",
            "year": "2005",
            "imdb": "7.0",
            "why": "Supernatural detective vs demons/angels; dark comic-book vibe.",
            "watch_hint": "Availability rotates — check JustWatch for your services.",
        },
        {
            "title": "Underworld",
            "year": "2003",
            "imdb": "7.0",
            "why": "Gothic action; vampires vs werewolves; stylish dark fantasy.",
            "watch_hint": "Availability rotates — check JustWatch for your services.",
        },
        {
            "title": "Hellboy",
            "year": "2004",
            "imdb": "6.9",
            "why": "Paranormal superhero/monster mythology; creature-feature energy.",
            "watch_hint": "Availability rotates — check JustWatch for your services.",
        },
    ]


def write_reco_suggestions(mem_root: Path, ymd: str, recos: list[dict]) -> Path:
    out_path = mem_root / "logs/system/predictions" / f"reco_suggestions_{ymd}.md"
    lines = [
        f"# Recommendation Suggestions – {ymd}",
        f"Generated: {iso_utc(utc_now())}",
        f"Agent: prediction_feed_agent.py {VERSION}",
        "",
        "These are **fallback recommendations** because your movie export has no 'Maybe/Candidate' entries.",
        "",
    ]
    for i, r in enumerate(recos, 1):
        lines.append(f"{i}. **{r['title']}** ({r['year']}) — IMDb {r['imdb']}")
        lines.append(f"   - Why: {r['why']}")
        lines.append(f"   - Watch: {r['watch_hint']}")
        lines.append("")
    write_text_atomic(out_path, "\n".join(lines).rstrip() + "\n")
    return out_path


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

    # Errands & Geofences (placeholder)
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
            f"2. [LOW] Breakdown: watched={counts.watched}, removed={counts.removed}, maybe={counts.maybe}, candidates={counts.candidates}, unknown={counts.unknown}."
        )
        lines.append("   - Reason: Derived from Status column in your export.")

        # picks from your list if they exist
        picks: list[str] = []
        for title, st in rows:
            s = st.lower()
            if "maybe" in s or "candidate" in s or "unwatched" in s or "to watch" in s or "queue" in s:
                picks.append(title)
            if len(picks) >= 5:
                break

        if not picks:
            # WOW fallback recos
            if counts.maybe == 0 and counts.candidates == 0:
                recos = fallback_recos()
                reco_path = write_reco_suggestions(mem_root, ymd, recos)

                lines.append("3. [MEDIUM] No 'Maybe/Candidate' titles found — here are 3 picks for tonight:")
                for r in recos:
                    lines.append(f"   - {r['title']} ({r['year']}) — IMDb {r['imdb']} — {r['why']}")
                lines.append(f"   - Reason: Your export is Watched/Removed only; suggestions logged to {reco_path}.")
            else:
                lines.append("3. [LOW] No unwatched candidates found in the export. If you want recommendations, add a few 'Maybe' titles to the sheets.")
                lines.append("   - Reason: Your export statuses are currently Watched/Removed only.")
        else:
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

    write_text_atomic(canonical_path, feed)
    print(f"Wrote (canonical): {canonical_path}")

    existing_mirror = safe_read_text(mirror_path)
    if existing_mirror:
        if normalize_for_compare(existing_mirror) == normalize_for_compare(feed):
            print(f"Mirror unchanged (ignoring Generated line): {mirror_path}")
            return 0

    write_text_atomic(mirror_path, feed)
    print(f"Mirrored (repo): {mirror_path}")
    return 0


# >>> STREAMING_AVAILABILITY_DIRECT_GATE_V2 >>>
import atexit as _r_streaming_atexit
from pathlib import Path as _RStreamingPath
from datetime import datetime as _RStreamingDatetime
import re as _r_streaming_re

def _rafael_streaming_availability_direct_gate_v2():
    mem_dir = _RStreamingPath("/home/rafa1215/memory/logs/system/predictions")
    repo_dir = _RStreamingPath("/home/rafa1215/consensus-project/memory/logs/system/predictions")
    today = _RStreamingDatetime.now().strftime("%Y-%m-%d")
    paths = [mem_dir / f"prediction_feed_{today}.md", repo_dir / f"prediction_feed_{today}.md"]

    allowed_platforms = [
        "Netflix", "Max", "Hulu", "Prime Video", "Paramount+", "Apple TV+",
        "Disney+", "Tubi", "Roku Channel", "Plex", "Hoopla", "Fawesome",
        "Freevee", "Fandango at Home Free"
    ]

    suppressed_titles = [
        "Constantine", "Underworld", "The Sandman", "Invincible",
        "Jupiter's Legacy", "The Dark Knight", "The Umbrella Academy",
        "Godzilla Minus One", "The Witch", "The Rip", "War Machine",
        "Troll 2", "Primitive War", "Blade", "Ghost Rider", "Spawn",
        "Predator: Badlands", "The Green Knight", "Sinners",
        "Dracula: A Love Tale"
    ]

    def has_streaming_proof(line):
        low = line.lower()
        has_platform = any(p.lower() in low for p in allowed_platforms)
        has_source = ("source:" in low) or ("verified:" in low) or ("justwatch" in low)
        has_date = ("checked:" in low) or ("date checked:" in low)
        rent_buy_only = ("rent" in low or "buy" in low) and not any(p.lower() in low for p in allowed_platforms)
        return has_platform and has_source and has_date and not rent_buy_only

    def has_suppressed_title(line):
        low = line.lower()
        return any(t.lower() in low for t in suppressed_titles)

    for path in paths:
        if not path.exists():
            continue

        original = path.read_text(errors="replace")
        lines = original.splitlines()
        out = []
        changed = False
        i = 0

        while i < len(lines):
            line = lines[i]
            low = line.lower()

            starts_movie_reco_block = (
                "here are 3 picks for tonight" in low
                or "recommended movies" in low
                or "movie recommendation" in low
                or "no 'maybe/candidate' titles found" in low
            )

            if starts_movie_reco_block:
                block = [line]
                j = i + 1
                while j < len(lines):
                    nxt = lines[j]
                    if j > i + 1 and (
                        _r_streaming_re.match(r"^\d+\.\s+\[[A-Z]+\]", nxt)
                        or nxt.startswith("## ")
                    ):
                        break
                    block.append(nxt)
                    j += 1

                movie_lines = [
                    b for b in block
                    if b.strip().startswith("-") and ("imdb" in b.lower() or "—" in b)
                ]

                missing_streaming_proof = bool(movie_lines) and not all(has_streaming_proof(b) for b in movie_lines)
                contains_suppressed_title = any(has_suppressed_title(b) for b in movie_lines)

                if missing_streaming_proof or contains_suppressed_title:
                    out.append("3. [LOW] Streaming recommendation gate blocked unverified movie picks.")
                    out.append("   - Reason: Movie suggestions must include verified current U.S. streaming platform, verification source, and date checked. Rent/buy-only, ambiguous, already-watched, or suppressed titles are rejected.")
                    changed = True
                    i = j
                    continue

            out.append(line)
            i += 1

        if changed:
            path.write_text("\n".join(out).rstrip() + "\n")
            audit = mem_dir / "streaming_gate_audit.log"
            audit.parent.mkdir(parents=True, exist_ok=True)
            with audit.open("a") as f:
                f.write(f"{_RStreamingDatetime.now().isoformat()} blocked_unverified_or_suppressed_movie_recommendations file={path}\n")

            mirror_audit = repo_dir / "streaming_gate_audit.log"
            mirror_audit.parent.mkdir(parents=True, exist_ok=True)
            try:
                mirror_audit.write_text(audit.read_text())
            except Exception:
                pass

_r_streaming_atexit.register(_rafael_streaming_availability_direct_gate_v2)
# <<< STREAMING_AVAILABILITY_DIRECT_GATE_V2 <<<


if __name__ == "__main__":
    sys.exit(main())

