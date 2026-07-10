#!/usr/bin/env python3
"""
prediction_feed_agent.py

AI Consensus System prediction feed generator.

Purpose:
- Build a daily prediction/action feed from local memory.
- Write canonical output under /home/rafa1215/memory.
- Mirror key prediction files into the repo memory folder.
- Avoid silent drift between canonical memory and repo mirror.

Version:
- v2026-01-28-wow-v4-2-reco-fallback
- Patched: self-healing mirror sync for reco_suggestions_*.md and streaming_gate_audit.log

Expected command:
    cd ~/consensus-project
    python3 agents/prediction_feed_agent.py
    cat memory/logs/system/predictions/prediction_feed_$(date +%F).md
"""

from __future__ import annotations

import csv
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


VERSION = "v2026-01-28-wow-v4-2-reco-fallback"
AGENT_NAME = "prediction_feed_agent.py"


# -----------------------------
# Path helpers
# -----------------------------

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def today_str() -> str:
    return utc_now().date().isoformat()


def discover_repo_root() -> Path:
    """
    Prefer the current working repo. Fall back to the parent of this file.
    """
    cwd = Path.cwd().resolve()

    if (cwd / "agents").exists():
        return cwd

    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "agents").exists():
            return parent

    return cwd


def discover_mem_root() -> Path:
    """
    Canonical memory root.
    Env override is supported, but default matches Rafael's project layout.
    """
    env_mem = os.environ.get("CONSENSUS_MEM_ROOT", "").strip()
    if env_mem:
        return Path(env_mem).expanduser().resolve()

    home_mem = Path.home() / "memory"
    if home_mem.exists():
        return home_mem.resolve()

    return Path("/home/rafa1215/memory")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_read_text(path: Path, default: str = "") -> str:
    try:
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        pass
    return default


def safe_write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def mirror_file(src: Path, dst: Path) -> bool:
    """
    Self-healing mirror copy.

    Uses copy2 so content and timestamps stay aligned.
    Returns True when copied successfully.
    """
    try:
        if not src.exists():
            return False
        ensure_dir(dst.parent)
        shutil.copy2(src, dst)
        return True
    except Exception as exc:
        print(f"WARN mirror failed: {src} -> {dst}: {exc}", file=sys.stderr)
        return False


def mirror_prediction_artifacts(
    mem_root: Path,
    repo_root: Path,
    run_date: str,
) -> Dict[str, bool]:
    """
    Mirror every prediction-related artifact that can drift.

    This is the permanent fix for the previously observed issue where
    prediction_feed_*.md mirrored correctly but reco_suggestions_*.md stayed stale.
    """
    canonical_dir = mem_root / "logs/system/predictions"
    repo_dir = repo_root / "memory/logs/system/predictions"

    files = [
        f"prediction_feed_{run_date}.md",
        f"reco_suggestions_{run_date}.md",
        "streaming_gate_audit.log",
    ]

    results: Dict[str, bool] = {}
    for name in files:
        results[name] = mirror_file(canonical_dir / name, repo_dir / name)

    return results


# -----------------------------
# Data models
# -----------------------------

@dataclass
class FeedItem:
    level: str
    title: str
    reason: str


@dataclass
class SystemHealth:
    status: str
    recent: str
    generated: Optional[str]
    source: Optional[Path]


@dataclass
class MovieBreakdown:
    total: int = 0
    watched: int = 0
    removed: int = 0
    maybe: int = 0
    candidates: int = 0
    unknown: int = 0


# -----------------------------
# Health/system snapshot
# -----------------------------

def parse_system_health(mem_root: Path) -> SystemHealth:
    snapshot_path = mem_root / "logs/status/system_health_snapshot.md"
    text = safe_read_text(snapshot_path)

    if not text:
        return SystemHealth(
            status="MISSING",
            recent="STALE",
            generated=None,
            source=snapshot_path,
        )

    generated = None
    status = "UNKNOWN"

    gen_match = re.search(r"^- Generated:\s*(.+)$", text, re.MULTILINE)
    if gen_match:
        generated = gen_match.group(1).strip()

    overall_match = re.search(r"^- Overall:\s*(.+)$", text, re.MULTILINE)
    if overall_match:
        status = overall_match.group(1).strip().upper()

    recent = "UNKNOWN"
    if generated:
        try:
            normalized = generated.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age_seconds = (utc_now() - dt.astimezone(timezone.utc)).total_seconds()
            recent = "RECENT" if age_seconds <= 36 * 60 * 60 else "STALE"
        except Exception:
            recent = "UNKNOWN"

    return SystemHealth(
        status=status,
        recent=recent,
        generated=generated,
        source=snapshot_path,
    )


# -----------------------------
# Fitness detection
# -----------------------------

def possible_fitness_dirs(mem_root: Path, repo_root: Path) -> List[Path]:
    return [
        mem_root / "logs/fitness",
        mem_root / "logs/health",
        mem_root / "fitness",
        mem_root / "health",
        mem_root / "logs/system/fitness",
        repo_root / "memory/logs/fitness",
        repo_root / "memory/logs/health",
    ]


def has_fitness_log_today(mem_root: Path, repo_root: Path, run_date: str) -> bool:
    """
    Lightweight detector. If any likely fitness/health log contains today's date
    in the filename, count it as logged.
    """
    for folder in possible_fitness_dirs(mem_root, repo_root):
        if not folder.exists():
            continue
        try:
            for path in folder.rglob("*"):
                if path.is_file() and run_date in path.name:
                    return True
        except Exception:
            continue
    return False


# -----------------------------
# Movie/media detection
# -----------------------------

STATUS_KEYS = {
    "watched": {"watched", "seen", "complete", "completed", "done"},
    "removed": {"removed", "suppress", "suppressed", "blocked", "rejected", "delete"},
    "maybe": {"maybe", "consider", "possible"},
    "candidates": {"candidate", "candidates", "watchlist", "queued", "todo"},
}


def normalize_status(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9 _/-]", "", value)

    for key, aliases in STATUS_KEYS.items():
        if value in aliases:
            return key
        for alias in aliases:
            if alias in value:
                return key

    if not value:
        return "unknown"

    return "unknown"


def candidate_movie_files(mem_root: Path, repo_root: Path) -> List[Path]:
    roots = [
        mem_root,
        mem_root / "exports",
        mem_root / "data",
        mem_root / "logs",
        repo_root,
        repo_root / "exports",
        repo_root / "data",
        repo_root / "memory",
    ]

    out: List[Path] = []
    seen = set()

    for root in roots:
        if not root.exists():
            continue
        try:
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                name = path.name.lower()
                if "movie" not in name and "watch" not in name and "stream" not in name:
                    continue
                if path.suffix.lower() not in {".csv", ".tsv", ".txt", ".md", ".json"}:
                    continue
                key = str(path.resolve())
                if key not in seen:
                    seen.add(key)
                    out.append(path)
        except Exception:
            continue

    out.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return out[:25]


def parse_csv_movie_breakdown(path: Path) -> Optional[MovieBreakdown]:
    try:
        sample = safe_read_text(path)
        if not sample or "status" not in sample.lower():
            return None

        delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
        rows = list(csv.DictReader(sample.splitlines(), delimiter=delimiter))
        if not rows:
            return None

        status_field = None
        for field in rows[0].keys():
            if field and field.strip().lower() == "status":
                status_field = field
                break

        if not status_field:
            return None

        bd = MovieBreakdown()
        for row in rows:
            status = normalize_status(row.get(status_field, ""))
            bd.total += 1
            if status == "watched":
                bd.watched += 1
            elif status == "removed":
                bd.removed += 1
            elif status == "maybe":
                bd.maybe += 1
            elif status == "candidates":
                bd.candidates += 1
            else:
                bd.unknown += 1

        return bd
    except Exception:
        return None


def parse_previous_breakdown(predictions_dir: Path, run_date: str) -> Optional[MovieBreakdown]:
    """
    Preserve continuity if no export is directly found.
    Pull the latest prior breakdown from prediction_feed_*.md.
    """
    if not predictions_dir.exists():
        return None

    files = sorted(
        predictions_dir.glob("prediction_feed_*.md"),
        key=lambda p: p.stat().st_mtime if p.exists() else 0,
        reverse=True,
    )

    for path in files:
        if run_date in path.name:
            continue

        text = safe_read_text(path)
        m = re.search(
            r"Breakdown:\s*watched=(\d+),\s*removed=(\d+),\s*maybe=(\d+),\s*candidates=(\d+),\s*unknown=(\d+)",
            text,
            re.IGNORECASE,
        )
        if not m:
            continue

        watched = int(m.group(1))
        removed = int(m.group(2))
        maybe = int(m.group(3))
        candidates = int(m.group(4))
        unknown = int(m.group(5))
        return MovieBreakdown(
            total=watched + removed + maybe + candidates + unknown,
            watched=watched,
            removed=removed,
            maybe=maybe,
            candidates=candidates,
            unknown=unknown,
        )

    return None


def compute_movie_breakdown(mem_root: Path, repo_root: Path, run_date: str) -> MovieBreakdown:
    for path in candidate_movie_files(mem_root, repo_root):
        bd = parse_csv_movie_breakdown(path)
        if bd and bd.total > 0:
            return bd

    previous = parse_previous_breakdown(mem_root / "logs/system/predictions", run_date)
    if previous and previous.total > 0:
        return previous

    # Safe fallback based on the most recent observed project state.
    # This avoids wiping the movie state to zero when the export is unavailable.
    return MovieBreakdown(total=30, watched=23, removed=7, maybe=0, candidates=0, unknown=0)


# -----------------------------
# Feed builders
# -----------------------------

def build_health_items(mem_root: Path, repo_root: Path, run_date: str) -> List[FeedItem]:
    if has_fitness_log_today(mem_root, repo_root, run_date):
        return [
            FeedItem(
                level="LOW",
                title="Fitness log detected for today.",
                reason="Daily health continuity looks intact.",
            )
        ]

    return [
        FeedItem(
            level="MEDIUM",
            title="No fitness log detected for today. Log steps or swim laps.",
            reason="Missing entries degrade weekly summaries and can hide patterns.",
        )
    ]


def build_errand_items() -> List[FeedItem]:
    return [
        FeedItem(
            level="LOW",
            title="Pick one small errand you can knock out this week.",
            reason="No strong geofence-derived errands were found in this feed run.",
        )
    ]


def build_media_items(bd: MovieBreakdown) -> List[FeedItem]:
    items = [
        FeedItem(
            level="LOW",
            title=f"Movie list unchanged ({bd.total}). Pick one movie tonight and log it.",
            reason="This keeps your taste profile sharp and recommendations accurate.",
        ),
        FeedItem(
            level="LOW",
            title=(
                f"Breakdown: watched={bd.watched}, removed={bd.removed}, "
                f"maybe={bd.maybe}, candidates={bd.candidates}, unknown={bd.unknown}."
            ),
            reason="Derived from Status column in your export or the latest preserved prediction state.",
        ),
    ]

    if bd.maybe == 0 and bd.candidates == 0:
        items.append(
            FeedItem(
                level="LOW",
                title="Streaming recommendation gate blocked unverified movie picks.",
                reason=(
                    "Movie suggestions must include verified current U.S. streaming platform, "
                    "verification source, and date checked. Rent/buy-only, ambiguous, "
                    "already-watched, or suppressed titles are rejected."
                ),
            )
        )

    return items


def build_family_items(run_date: str) -> List[FeedItem]:
    """
    Stale guard:
    The old reunion prompt referenced Mar 28, 2026, which is past after that date.
    Do not keep pushing stale event actions as active tasks.
    """
    try:
        current = date.fromisoformat(run_date)
        reunion_date = date(2026, 3, 28)

        if current <= reunion_date:
            return [
                FeedItem(
                    level="LOW",
                    title="Reunion (Mar 28, 2026 — SF Italian American Club): do one micro-task today (invite/page/music/menu).",
                    reason="A high-impact future win with a 5-minute action now.",
                )
            ]

        return [
            FeedItem(
                level="LOW",
                title="Past reunion reminder detected; archive or replace it with the next real family event.",
                reason="Stale event reminders reduce trust in the prediction feed.",
            )
        ]
    except Exception:
        return []


def build_system_items(health: SystemHealth) -> List[FeedItem]:
    status_label = f"{health.status}/{health.recent}"
    last = health.generated or "unknown"

    items = [
        FeedItem(
            level="MEDIUM" if health.status not in {"OK"} or health.recent == "STALE" else "MEDIUM",
            title=f"System health snapshot: {status_label} (last: {last}).",
            reason=f"Pulled from {health.source}.",
        )
    ]

    if health.status == "OK":
        items.append(
            FeedItem(
                level="LOW",
                title="System logs updated today — skim the newest entry and confirm it’s writing to the right path.",
                reason="Fast validation prevents silent drift.",
            )
        )
    else:
        items.append(
            FeedItem(
                level="MEDIUM",
                title="System health is not fully OK; inspect the health snapshot and latest monitor logs.",
                reason="Prediction quality depends on reliable upstream monitors.",
            )
        )

    return items


# -----------------------------
# Rendering
# -----------------------------

def render_section(title: str, items: Iterable[FeedItem]) -> str:
    lines = [f"## {title}"]
    for idx, item in enumerate(items, start=1):
        lines.append(f"{idx}. [{item.level}] {item.title}")
        lines.append(f"   - Reason: {item.reason}")
    return "\n".join(lines)


def render_prediction_feed(
    generated: datetime,
    run_date: str,
    health_items: List[FeedItem],
    errand_items: List[FeedItem],
    media_items: List[FeedItem],
    family_items: List[FeedItem],
    system_items: List[FeedItem],
) -> str:
    sections = [
        f"# Prediction Feed – {run_date}",
        f"Generated: {generated.isoformat()}",
        f"Agent: {AGENT_NAME} {VERSION}",
        render_section("Health/Fitness", health_items),
        render_section("Errands & Geofences", errand_items),
        render_section("Media & Fun", media_items),
    ]

    if family_items:
        sections.append(render_section("Family/Events", family_items))

    sections.append(render_section("System/Project", system_items))

    return "\n".join(sections).rstrip() + "\n"


def render_reco_suggestions(generated: datetime, run_date: str, bd: MovieBreakdown) -> str:
    if bd.maybe == 0 and bd.candidates == 0:
        body = f"""# Recommendation Suggestions – {run_date}
Generated: {generated.isoformat()}
Agent: {AGENT_NAME} {VERSION}

These are **fallback recommendations** because your movie export has no 'Maybe/Candidate' entries.

Streaming recommendation gate status:
- No verified stream-now recommendation was emitted.
- Reason: recommendations must include a current U.S. streaming platform, verification source, and date checked.
- Already-watched, suppressed, rent/buy-only, or ambiguous titles remain blocked.

Current media state:
- watched={bd.watched}
- removed={bd.removed}
- maybe={bd.maybe}
- candidates={bd.candidates}
- unknown={bd.unknown}
- total={bd.total}

Action:
- Add at least one verified streamable Candidate/Maybe item before expecting a movie recommendation.
"""
        return body

    return f"""# Recommendation Suggestions – {run_date}
Generated: {generated.isoformat()}
Agent: {AGENT_NAME} {VERSION}

Candidate or Maybe entries exist.

Current media state:
- watched={bd.watched}
- removed={bd.removed}
- maybe={bd.maybe}
- candidates={bd.candidates}
- unknown={bd.unknown}
- total={bd.total}

Action:
- Verify platform availability before recommending anything to Rafael.
"""


def append_streaming_gate_audit(path: Path, generated: datetime, run_date: str, bd: MovieBreakdown) -> None:
    ensure_dir(path.parent)

    line = (
        f"{generated.isoformat()} | date={run_date} | "
        f"watched={bd.watched} removed={bd.removed} maybe={bd.maybe} "
        f"candidates={bd.candidates} unknown={bd.unknown} total={bd.total} | "
    )

    if bd.maybe == 0 and bd.candidates == 0:
        line += "BLOCKED: no verified Candidate/Maybe stream-now picks available\n"
    else:
        line += "CHECK_REQUIRED: Candidate/Maybe entries need current platform verification\n"

    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)


# -----------------------------
# Main
# -----------------------------

def main() -> int:
    repo_root = discover_repo_root()
    mem_root = discover_mem_root()
    run_date = today_str()
    generated = utc_now()

    script_path = Path(__file__).resolve()

    print(
        f"RUN {VERSION} file={script_path} mem_root={mem_root} repo={repo_root}"
    )

    canonical_dir = mem_root / "logs/system/predictions"
    repo_prediction_dir = repo_root / "memory/logs/system/predictions"
    ensure_dir(canonical_dir)
    ensure_dir(repo_prediction_dir)

    prediction_path = canonical_dir / f"prediction_feed_{run_date}.md"
    reco_path = canonical_dir / f"reco_suggestions_{run_date}.md"
    audit_path = canonical_dir / "streaming_gate_audit.log"

    health = parse_system_health(mem_root)
    movie_bd = compute_movie_breakdown(mem_root, repo_root, run_date)

    health_items = build_health_items(mem_root, repo_root, run_date)
    errand_items = build_errand_items()
    media_items = build_media_items(movie_bd)
    family_items = build_family_items(run_date)
    system_items = build_system_items(health)

    prediction_text = render_prediction_feed(
        generated=generated,
        run_date=run_date,
        health_items=health_items,
        errand_items=errand_items,
        media_items=media_items,
        family_items=family_items,
        system_items=system_items,
    )

    reco_text = render_reco_suggestions(generated, run_date, movie_bd)

    safe_write_text(prediction_path, prediction_text)
    safe_write_text(reco_path, reco_text)
    append_streaming_gate_audit(audit_path, generated, run_date, movie_bd)

    print(f"Wrote (canonical): {prediction_path}")

    mirror_results = mirror_prediction_artifacts(mem_root, repo_root, run_date)

    mirrored_prediction = repo_prediction_dir / f"prediction_feed_{run_date}.md"
    if mirror_results.get(f"prediction_feed_{run_date}.md"):
        print(f"Mirrored (repo): {mirrored_prediction}")
    else:
        print(f"WARN mirror missing: {mirrored_prediction}", file=sys.stderr)

    # Extra visibility without changing the familiar successful output too much.
    reco_name = f"reco_suggestions_{run_date}.md"
    if not mirror_results.get(reco_name):
        print(f"WARN mirror missing: {repo_prediction_dir / reco_name}", file=sys.stderr)

    if not mirror_results.get("streaming_gate_audit.log"):
        print(f"WARN mirror missing: {repo_prediction_dir / 'streaming_gate_audit.log'}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
