#!/usr/bin/env python3
"""Prediction Feed Agent v2026-07-10-smart-feed-v1.

Drop-in replacement for agents/prediction_feed_agent.py.

Goals:
- Preserve canonical + repository mirror output behavior.
- Avoid false "missing fitness" alerts by checking several sources.
- Replace generic errand filler with grounded, source-backed actions.
- Produce a useful media summary instead of opaque counts.
- Automatically suppress/archive stale family reminders in the feed.
- Explain system-health warnings and provide concrete next commands.
- Add conservative, evidence-based 24–72 hour predictions.
- Never fabricate a recommendation when required evidence is absent.

This module uses only the Python standard library.
"""
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Sequence

VERSION = "v2026-07-10-smart-feed-v1.1"
STALE_EVENT_DAYS = int(os.getenv("PREDICTION_STALE_EVENT_DAYS", "14"))
HEALTH_STALE_MINUTES = int(os.getenv("PREDICTION_HEALTH_STALE_MINUTES", "180"))


@dataclass(frozen=True)
class Finding:
    section: str
    confidence: str
    message: str
    reason: str
    action: str | None = None
    evidence: tuple[str, ...] = ()


@dataclass
class Context:
    now: datetime
    repo_root: Path
    memory_root: Path
    findings: list[Finding] = field(default_factory=list)

    @property
    def today(self) -> date:
        return self.now.date()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_datetime(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    for candidate in (value, value.replace(" ", "T")):
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            pass
    return None


def safe_read(path: Path, max_bytes: int = 2_000_000) -> str:
    try:
        if not path.is_file() or path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def recent_files(roots: Sequence[Path], patterns: Sequence[str], days: int = 14) -> list[Path]:
    cutoff = utc_now().timestamp() - days * 86400
    result: dict[str, Path] = {}
    for root in roots:
        if not root.exists():
            continue
        for pattern in patterns:
            try:
                for path in root.glob(pattern):
                    try:
                        if path.is_file() and path.stat().st_mtime >= cutoff:
                            result[str(path.resolve())] = path
                    except OSError:
                        continue
            except OSError:
                continue
    return sorted(result.values(), key=lambda p: p.stat().st_mtime, reverse=True)


def contains_today(text: str, today: date) -> bool:
    forms = {
        today.isoformat(),
        today.strftime("%m/%d/%Y"),
        today.strftime("%-m/%-d/%Y") if os.name != "nt" else today.strftime("%#m/%#d/%Y"),
        today.strftime("%B %-d, %Y") if os.name != "nt" else today.strftime("%B %#d, %Y"),
    }
    lowered = text.lower()
    return any(form.lower() in lowered for form in forms)


def extract_number(text: str, labels: Sequence[str]) -> float | None:
    joined = "|".join(re.escape(label) for label in labels)
    match = re.search(rf"(?:{joined})\s*[:=\-]?\s*([\d,]+(?:\.\d+)?)", text, re.I)
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", ""))
    except ValueError:
        return None


def git_root(start: Path) -> Path:
    try:
        value = subprocess.check_output(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
        ).strip()
        return Path(value)
    except Exception:
        return start


def resolve_roots() -> tuple[Path, Path]:
    script = Path(__file__).resolve()
    repo_root = Path(os.getenv("CONSENSUS_REPO_ROOT", "")).expanduser() if os.getenv("CONSENSUS_REPO_ROOT") else git_root(script.parent)
    memory_root = Path(os.getenv("CONSENSUS_MEMORY_ROOT", "~/memory")).expanduser()
    return repo_root, memory_root



def detect_fitness(ctx: Context) -> None:
    """Find genuine current-day fitness measurements, not system-log mentions."""
    roots = [
        ctx.memory_root / "logs/fitness",
        ctx.memory_root / "logs/health",
        ctx.memory_root / "fitness",
        ctx.memory_root / "health",
        ctx.repo_root / "memory/logs/fitness",
        ctx.repo_root / "memory/logs/health",
        ctx.repo_root / "memory/exports",
    ]
    files = recent_files(
        roots,
        [
            "**/*fitness*.*", "**/*fitbit*.*", "**/*coros*.*",
            "**/*steps*.*", "**/*swim*.*", "**/*workout*.*", "**/*activity*.*",
        ],
        days=8,
    )
    evidence: list[str] = []
    steps: float | None = None
    laps: float | None = None
    workout_found = False
    excluded_path_terms = (
        "/archive/", "/status/", "/system/", "system_health",
        "integration.log", "monitor", "diagnostic", "snapshot",
    )
    workout_terms = (
        "workout completed", "completed workout", "swim completed",
        "exercise completed", "activity completed", "stationary bike", "pool workout",
    )
    for candidate in files[:100]:
        normalized_path = str(candidate).lower().replace("\\\\", "/")
        if any(term in normalized_path for term in excluded_path_terms):
            continue
        body = safe_read(candidate)
        if not body or not contains_today(body, ctx.today):
            continue
        found_steps = extract_number(body, ["steps", "step count", "daily steps", "total steps"])
        found_laps = extract_number(body, ["laps", "swim laps", "pool laps", "running laps"])
        explicit_workout = any(term in body.lower() for term in workout_terms)
        if found_steps is None and found_laps is None and not explicit_workout:
            continue
        if found_steps is not None:
            steps = max(steps or 0, found_steps)
        if found_laps is not None:
            laps = max(laps or 0, found_laps)
        workout_found = workout_found or explicit_workout
        evidence.append(str(candidate))
    if evidence:
        details: list[str] = []
        if steps is not None:
            details.append(f"{steps:,.0f} steps")
        if laps is not None:
            details.append(f"{laps:,.0f} swim laps")
        if workout_found and not details:
            details.append("completed workout")
        ctx.findings.append(Finding(
            "Health/Fitness", "HIGH",
            f"Today's fitness log was found ({', '.join(details)}).",
            "A genuine current-day measurement or completed workout was found.",
            evidence=tuple(evidence[:4]),
        ))
    else:
        ctx.findings.append(Finding(
            "Health/Fitness", "MEDIUM", "No current-day fitness measurement was found.",
            "The agent checked Fitbit, COROS, steps, swim and workout sources while excluding system-health and archived logs.",
            "Sync a wearable or add today's step count or swim laps.",
        ))

def parse_task_lines(text: str) -> list[str]:
    tasks: list[str] = []
    for raw in text.splitlines():
        line = re.sub(r"^\s*(?:[-*]|\d+[.)]|\[[ xX]\])\s*", "", raw).strip()
        if len(line) < 5 or len(line) > 180:
            continue
        low = line.lower()
        if any(word in low for word in ("todo", "buy", "pick up", "return", "errand", "shopping", "appointment", "due")):
            tasks.append(line)
    return tasks


def detect_errands(ctx: Context) -> None:
    roots = [ctx.memory_root, ctx.repo_root / "memory"]
    files = recent_files(roots, ["**/*todo*.*", "**/*errand*.*", "**/*shopping*.*", "**/*calendar*.*", "**/*delivery*.*", "**/*reminder*.*"], days=21)
    grounded: list[tuple[str, str]] = []
    for path in files[:60]:
        for task in parse_task_lines(safe_read(path)):
            grounded.append((task, str(path)))
            if len(grounded) >= 5:
                break
        if len(grounded) >= 5:
            break
    if grounded:
        task, source = grounded[0]
        ctx.findings.append(Finding(
            "Errands & Geofences", "MEDIUM", f"Grounded next errand: {task}",
            "This action came from an existing task, shopping, delivery, calendar, or reminder source rather than a generic fallback.",
            "Complete it, reschedule it, or mark it done so it does not recur.", (source,),
        ))
    else:
        ctx.findings.append(Finding(
            "Errands & Geofences", "LOW", "No actionable errands were detected.",
            "No grounded shopping-list, calendar, delivery, geofence, or task item was found; the old 'pick one small errand' filler was intentionally removed.",
        ))



def read_movie_status(ctx: Context) -> dict[str, int | str]:
    """Read movie state from CSV, JSON, Markdown or text exports."""
    roots = [ctx.memory_root, ctx.repo_root / "memory", ctx.repo_root]
    files = recent_files(
        roots,
        [
            "**/*movie*.csv", "**/*media*.csv", "**/*watch*.csv",
            "**/*movie*.json", "**/*media*.json", "**/*movie*.md",
            "**/*movie*.txt", "**/*watch*.txt", "**/movie_list_export.txt",
        ],
        days=365,
    )
    counts: dict[str, int | str] = {
        "watched": 0, "removed": 0, "maybe": 0,
        "candidates": 0, "unknown": 0, "last_watched": "Not available",
    }
    seen_records: set[tuple[str, str]] = set()
    newest_watched_time = 0.0
    status_aliases = {
        "watched": {"watched", "seen", "finished", "complete", "completed", "done"},
        "removed": {"removed", "suppressed", "suppress", "rejected", "skip", "skipped", "blocked", "deleted"},
        "maybe": {"maybe", "considering", "consider", "possible"},
        "candidates": {"candidate", "candidates", "recommended", "available", "queued", "watchlist", "to watch", "unwatched"},
    }
    def classify(raw_status: str) -> str:
        cleaned = re.sub(r"[^a-z0-9 ]+", " ", raw_status.lower())
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        for category, aliases in status_aliases.items():
            if cleaned in aliases:
                return category
        for category, aliases in status_aliases.items():
            if any(alias in cleaned for alias in aliases):
                return category
        return "unknown"
    def add_record(title: str, status: str, source: Path) -> None:
        nonlocal newest_watched_time
        title = title.strip().strip("|,;:-") or "Untitled"
        category = classify(status)
        key = (title.lower(), category)
        if key in seen_records:
            return
        seen_records.add(key)
        counts[category] = int(counts[category]) + 1
        if category == "watched":
            try:
                modified = source.stat().st_mtime
            except OSError:
                modified = 0
            if modified >= newest_watched_time:
                newest_watched_time = modified
                counts["last_watched"] = title
    for source in files[:80]:
        body = safe_read(source)
        if not body:
            continue
        try:
            if source.suffix.lower() == ".json":
                parsed = json.loads(body)
                entries = parsed.get("movies", parsed.get("items", parsed.get("records", []))) if isinstance(parsed, dict) else parsed
                if isinstance(entries, list):
                    for entry in entries:
                        if isinstance(entry, dict):
                            normalized = {str(k).lower().strip(): str(v or "").strip() for k, v in entry.items()}
                            add_record(normalized.get("title", normalized.get("name", "Untitled")), normalized.get("status", normalized.get("state", "unknown")), source)
                continue
            lines = body.splitlines()
            first_line = lines[0] if lines else ""
            delimiter = "\t" if "\t" in first_line else "|" if "|" in first_line else ","
            rows = list(csv.DictReader(lines, delimiter=delimiter))
            usable_rows = False
            for row in rows:
                normalized = {str(k or "").lower().strip(): str(v or "").strip() for k, v in row.items()}
                status = normalized.get("status", normalized.get("state", ""))
                title = normalized.get("title", normalized.get("movie", normalized.get("name", "")))
                if status:
                    usable_rows = True
                    add_record(title, status, source)
            if usable_rows:
                continue
        except (ValueError, csv.Error, json.JSONDecodeError):
            pass
        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line or len(line) > 500:
                continue
            status_match = re.search(
                r"\b(watched|seen|finished|complete|completed|done|removed|suppressed|rejected|skipped|blocked|maybe|considering|candidate|recommended|available|queued|watchlist)\b",
                line, re.IGNORECASE,
            )
            if not status_match:
                continue
            status = status_match.group(1)
            title = re.sub(r"^\s*\d+[.)]\s*", "", line[:status_match.start()]).strip(" |,;:-[]()")
            if title.lower() in {"", "status", "movie", "movies", "title", "breakdown"}:
                continue
            add_record(title, status, source)
    tracked = sum(int(counts[k]) for k in ("watched", "removed", "maybe", "candidates", "unknown"))
    if tracked == 0:
        previous_files = recent_files([
            ctx.memory_root / "logs/system/predictions",
            ctx.repo_root / "memory/logs/system/predictions",
        ], ["prediction_feed_*.md"], days=365)
        for previous in previous_files:
            match = re.search(
                r"Breakdown:\s*watched=(\d+),\s*removed=(\d+),\s*maybe=(\d+),\s*candidates=(\d+),\s*unknown=(\d+)",
                safe_read(previous), re.IGNORECASE,
            )
            if match:
                counts["watched"] = int(match.group(1))
                counts["removed"] = int(match.group(2))
                counts["maybe"] = int(match.group(3))
                counts["candidates"] = int(match.group(4))
                counts["unknown"] = int(match.group(5))
                break
    return counts

def detect_media(ctx: Context) -> None:
    c = read_movie_status(ctx)
    total = sum(int(c[k]) for k in ("watched", "removed", "maybe", "candidates", "unknown"))
    ctx.findings.append(Finding(
        "Media & Fun", "HIGH" if total else "LOW",
        f"Media summary: tracked={total}, watched={c['watched']}, suppressed/removed={c['removed']}, maybe={c['maybe']}, candidates={c['candidates']}, unknown={c['unknown']}; last watched={c['last_watched']}.",
        "The feed now exposes meaningful status totals instead of only reporting that the list is unchanged.",
        "Refresh the verified U.S. streaming catalog only when candidates reach zero." if int(c["candidates"]) == 0 else None,
    ))
    if int(c["candidates"]) == 0:
        ctx.findings.append(Finding(
            "Media & Fun", "MEDIUM", "No verified streaming candidate is currently available.",
            "The recommendation gate correctly rejects rent/buy-only, ambiguous, watched, suppressed, or unverified titles.",
            "Run the streaming-verification source refresh; do not bypass the gate with an unverified title.",
        ))


def dated_lines(text: str) -> Iterable[tuple[date, str]]:
    date_patterns = [r"(20\d{2}-\d{2}-\d{2})", r"(\d{1,2}/\d{1,2}/20\d{2})"]
    for line in text.splitlines():
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if not match:
                continue
            raw = match.group(1)
            try:
                parsed = datetime.strptime(raw, "%Y-%m-%d").date() if "-" in raw else datetime.strptime(raw, "%m/%d/%Y").date()
                yield parsed, line.strip()
            except ValueError:
                pass
            break



def detect_family_events(ctx: Context) -> None:
    """Detect only real family events, not event-related system logs."""
    roots = [ctx.memory_root, ctx.repo_root / "memory"]
    files = recent_files(
        roots,
        ["**/*family*.*", "**/*reunion*.*", "**/*birthday*.*", "**/*anniversary*.*", "**/*reminder*.*"],
        days=365,
    )
    stale: list[tuple[date, str, Path]] = []
    future: list[tuple[date, str, Path]] = []
    family_terms = ("family", "reunion", "birthday", "anniversary", "maribel", "asia", "rafael", "wedding", "graduation")
    excluded_terms = ("created missing log", "event_sync", "event sync", "sync_guard", "sync guard", "system event", "log file", "monitor", "diagnostic", "health snapshot", "archived")
    excluded_path_terms = ("/logs/archive/", "/logs/status/", "/logs/system/", "event_sync_guard", "system_health", "monitor", "diagnostic")
    for source in files[:100]:
        normalized_path = str(source).lower().replace("\\\\", "/")
        if any(term in normalized_path for term in excluded_path_terms):
            continue
        for when, line in dated_lines(safe_read(source)):
            lowered = line.lower()
            if any(term in lowered for term in excluded_terms):
                continue
            if not any(term in lowered for term in family_terms):
                continue
            age_days = (ctx.today - when).days
            if age_days > STALE_EVENT_DAYS:
                stale.append((when, line, source))
            elif when >= ctx.today:
                future.append((when, line, source))
    if future:
        when, line, source = sorted(future, key=lambda item: item[0])[0]
        ctx.findings.append(Finding(
            "Family/Events", "MEDIUM", f"Next dated family event: {line}",
            "A current or future family-specific event was found.", evidence=(str(source),),
        ))
    elif stale:
        when, line, source = sorted(stale, key=lambda item: item[0], reverse=True)[0]
        ctx.findings.append(Finding(
            "Family/Events", "LOW", f"Suppressed stale family reminder dated {when.isoformat()}.",
            f"The family event is more than {STALE_EVENT_DAYS} days old.",
            "Archive or update the source reminder during memory maintenance.", (str(source),),
        ))
    else:
        ctx.findings.append(Finding(
            "Family/Events", "LOW", "No current family event requires action.",
            "No valid current or future family-specific reminder was found.",
        ))

def health_snapshot_path(ctx: Context) -> Path | None:
    candidates = [
        ctx.memory_root / "logs/status/system_health_snapshot.md",
        ctx.repo_root / "memory/logs/status/system_health_snapshot.md",
    ]
    return next((p for p in candidates if p.is_file()), None)


def summarize_health(text: str) -> tuple[str, datetime | None, list[str], list[str]]:
    status = "UNKNOWN"
    updated: datetime | None = None
    problems: list[str] = []
    commands: list[str] = []
    status_match = re.search(r"(?:overall\s+)?status\s*[:=]\s*([A-Z][A-Z_/-]+)", text, re.I)
    if status_match:
        status = status_match.group(1).upper()
    else:
        token = re.search(r"\b(OK|WARN(?:ING)?|ERROR|FAIL(?:ED)?|CRITICAL|DEGRADED)\b", text, re.I)
        if token:
            status = token.group(1).upper()
    for match in re.finditer(r"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?", text):
        dt = parse_datetime(match.group(0))
        if dt and (updated is None or dt > updated):
            updated = dt
    for raw in text.splitlines():
        line = re.sub(r"^\s*[-*#>]+\s*", "", raw).strip()
        low = line.lower()
        if 4 <= len(line) <= 220 and any(k in low for k in ("warn", "error", "fail", "missing", "stale", "expired", "delayed", "unhealthy", "down")):
            if not low.startswith(("status:", "overall status:")):
                problems.append(line)
        if re.search(r"\b(?:python3?|bash|systemctl|journalctl|tail|cat)\b", line):
            commands.append(line.strip("` "))
    return status, updated, list(dict.fromkeys(problems))[:5], list(dict.fromkeys(commands))[:5]


def detect_system_health(ctx: Context) -> None:
    path = health_snapshot_path(ctx)
    if not path:
        ctx.findings.append(Finding(
            "System/Project", "MEDIUM", "System-health snapshot is missing.",
            "The feed cannot assess upstream reliability without the expected snapshot.",
            "Run the health monitor that writes memory/logs/status/system_health_snapshot.md.",
        ))
        return
    text = safe_read(path)
    status, updated, problems, commands = summarize_health(text)
    age_minutes = None if updated is None else max(0, int((ctx.now - updated).total_seconds() // 60))
    freshness = "unknown age" if age_minutes is None else f"{age_minutes} minutes old"
    problem_text = "; ".join(problems) if problems else "The snapshot does not state the component-level cause."
    action = commands[0] if commands else "Open the snapshot and latest monitor log; repair the first failing upstream component, then rerun this feed."
    confidence = "HIGH" if status in ("ERROR", "FAILED", "FAIL", "CRITICAL") else "MEDIUM"
    ctx.findings.append(Finding(
        "System/Project", confidence,
        f"System health: {status} ({freshness}). Details: {problem_text}",
        "The prediction feed now extracts warning details from the health snapshot instead of emitting only WARN/RECENT.",
        action, (str(path),),
    ))
    if age_minutes is not None and age_minutes > HEALTH_STALE_MINUTES:
        ctx.findings.append(Finding(
            "System/Project", "MEDIUM", f"Health snapshot is stale ({age_minutes} minutes old).",
            f"Freshness exceeded the configured {HEALTH_STALE_MINUTES}-minute threshold.",
            "Run the system-health monitor before trusting downstream predictions.", (str(path),),
        ))


def add_predictions(ctx: Context) -> None:
    # Conservative predictions derived only from findings already established.
    no_fitness = any(f.section == "Health/Fitness" and f.message.startswith("No current-day") for f in ctx.findings)
    no_candidates = any(f.section == "Media & Fun" and "No verified streaming candidate" in f.message for f in ctx.findings)
    unhealthy = any(f.section == "System/Project" and re.search(r"health: (WARN|ERROR|FAIL|CRITICAL|DEGRADED)", f.message, re.I) for f in ctx.findings)
    if no_fitness:
        ctx.findings.append(Finding(
            "24–72 Hour Predictions", "MEDIUM", "Today's activity summary is likely to remain incomplete unless a wearable sync or manual log arrives.",
            "No current-day activity record was found across all configured sources.",
            "Sync or log activity before the nightly summary runs.",
        ))
    if no_candidates:
        ctx.findings.append(Finding(
            "24–72 Hour Predictions", "HIGH", "The next movie recommendation run will likely return no pick.",
            "There are zero verified candidates and the streaming gate is correctly blocking unsupported choices.",
            "Refresh verified U.S. streaming availability before the next recommendation cycle.",
        ))
    if unhealthy:
        ctx.findings.append(Finding(
            "24–72 Hour Predictions", "MEDIUM", "Prediction quality may remain degraded until the upstream health warning is cleared.",
            "At least one current system-health finding is not OK.",
            "Resolve the first named health failure and rerun the health snapshot before relying on forecasts.",
        ))
    if not any(f.section == "24–72 Hour Predictions" for f in ctx.findings):
        ctx.findings.append(Finding(
            "24–72 Hour Predictions", "LOW", "No evidence-backed risk crossed the prediction threshold.",
            "The agent intentionally avoids speculative forecasts when supporting data is absent.",
        ))


def render(ctx: Context) -> str:
    generated = ctx.now.isoformat()
    lines = [
        f"# Prediction Feed – {ctx.today.isoformat()}",
        f"Generated: {generated}",
        f"Agent: prediction_feed_agent.py {VERSION}",
        "",
    ]
    section_order = ["Health/Fitness", "Errands & Geofences", "Media & Fun", "Family/Events", "System/Project", "24–72 Hour Predictions"]
    for section in section_order:
        entries = [f for f in ctx.findings if f.section == section]
        if not entries:
            continue
        lines.append(f"## {section}")
        for i, item in enumerate(entries, 1):
            lines.append(f"{i}. [{item.confidence}] {item.message}")
            lines.append(f"   - Reason: {item.reason}")
            if item.action:
                lines.append(f"   - Action: {item.action}")
            if item.evidence:
                lines.append("   - Evidence: " + "; ".join(item.evidence))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    repo_root, memory_root = resolve_roots()
    now = utc_now()
    ctx = Context(now=now, repo_root=repo_root, memory_root=memory_root)
    print(f"RUN {VERSION} file={Path(__file__).resolve()} mem_root={memory_root} repo={repo_root}")
    for detector in (detect_fitness, detect_errands, detect_media, detect_family_events, detect_system_health):
        try:
            detector(ctx)
        except Exception as exc:  # one broken source must not kill the whole feed
            ctx.findings.append(Finding(
                "System/Project", "MEDIUM", f"Detector {detector.__name__} failed safely: {type(exc).__name__}.",
                "The feed continued running so one malformed source could not block all predictions.",
                f"Inspect {detector.__name__} input files and rerun.",
            ))
    add_predictions(ctx)
    content = render(ctx)
    filename = f"prediction_feed_{ctx.today.isoformat()}.md"
    canonical = memory_root / "logs/system/predictions" / filename
    mirror = repo_root / "memory/logs/system/predictions" / filename
    atomic_write(canonical, content)
    print(f"Wrote (canonical): {canonical}")
    try:
        if canonical.resolve() != mirror.resolve():
            atomic_write(mirror, content)
        print(f"Mirrored (repo): {mirror}")
    except OSError as exc:
        print(f"WARN mirror failed: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
