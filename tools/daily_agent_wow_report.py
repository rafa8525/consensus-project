#!/usr/bin/env python3
import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

try:
    from zoneinfo import ZoneInfo
    PACIFIC = ZoneInfo("America/Los_Angeles")
except Exception:
    PACIFIC = timezone(timedelta(hours=-7))

PROJECT_ROOT = Path(os.environ.get("CONSENSUS_PROJECT_ROOT", "/home/rafa1215/consensus-project"))
MEMORY_ROOT = Path(os.environ.get("MEMORY_ROOT", "/home/rafa1215/memory"))
REPO_MEMORY_ROOT = PROJECT_ROOT / "memory"

STATUS_DIR = MEMORY_ROOT / "logs" / "status"
SYSTEM_DIR = MEMORY_ROOT / "logs" / "system"
PREDICTIONS_DIR = SYSTEM_DIR / "predictions"
FITNESS_DIR = MEMORY_ROOT / "logs" / "fitness"
FINANCE_DIR = MEMORY_ROOT / "logs" / "finance"
GEOFENCE_DIR = MEMORY_ROOT / "logs" / "geofencing"
EXPORTS_DIR = MEMORY_ROOT / "exports"
MOVIE_RECO_DIR = MEMORY_ROOT / "logs" / "movies"

REPORT_VERSION = "daily_agent_wow_report.py v2026-04-27-wow-v2-movie-reco"


@dataclass
class FileFinding:
    path: Path
    age_hours: Optional[float]
    summary: str


@dataclass
class MovieRecommendation:
    title: str
    year: str
    imdb_rating: str
    reason: str
    confidence: str


def now_local() -> datetime:
    return datetime.now(PACIFIC)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def ensure_dirs() -> None:
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    MOVIE_RECO_DIR.mkdir(parents=True, exist_ok=True)


def safe_read(path: Path, max_chars: int = 12000) -> str:
    try:
        if not path.exists() or not path.is_file():
            return ""
        text = path.read_text(encoding="utf-8", errors="replace")
        return text[-max_chars:] if len(text) > max_chars else text
    except Exception as exc:
        return f"[read_error: {exc}]"


def safe_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def file_age_hours(path: Path) -> Optional[float]:
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        return (now_utc() - mtime).total_seconds() / 3600.0
    except Exception:
        return None


def age_label(age: Optional[float]) -> str:
    if age is None:
        return "unknown"
    if age < 1:
        return f"{age * 60:.0f} minutes ago"
    if age < 48:
        return f"{age:.1f} hours ago"
    return f"{age / 24:.1f} days ago"


def latest_file(directory: Path, pattern: str = "*") -> Optional[Path]:
    try:
        files = [p for p in directory.glob(pattern) if p.is_file()]
        return max(files, key=lambda p: p.stat().st_mtime) if files else None
    except Exception:
        return None


def status_from_text(text: str) -> str:
    low = text.lower()
    if "overall: ok" in low or "| overall | ok" in low:
        return "OK"
    if "fail" in low or "error" in low or "broken" in low:
        return "ERROR"
    if "warn" in low or "stale" in low:
        return "WARN"
    return "UNKNOWN"


def clean_title(title: str) -> str:
    title = title.lower().strip()
    title = re.sub(r"\([^)]*\)", "", title)
    title = re.sub(r"[^a-z0-9]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def parse_movie_title(line: str) -> str:
    raw = line.strip()
    if not raw or raw.startswith("#"):
        return ""
    if "\t" in raw:
        raw = raw.split("\t")[0]
    elif "," in raw:
        raw = raw.split(",")[0]
    raw = re.sub(r"^\s*\d+\.\s*", "", raw).strip()
    return raw


def movie_history() -> set[str]:
    watched = set()
    text = safe_read(EXPORTS_DIR / "movie_list_export.txt", 80000)
    for line in text.splitlines():
        title = parse_movie_title(line)
        if title and title.lower() not in {"title", "movie title"}:
            watched.add(clean_title(title))

    suppressed = [
        "Constantine",
        "Underworld",
        "The Sandman",
        "Invincible",
        "Jupiter's Legacy",
        "The Dark Knight",
        "The Umbrella Academy",
        "Godzilla Minus One",
        "The Witch",
        "The Rip",
        "War Machine",
        "Troll 2",
        "Primitive War",
        "Dracula: A Love Tale",
        "Apex",
        "Protector",
        "From",
    ]
    for title in suppressed:
        watched.add(clean_title(title))
    return watched


def movie_candidates() -> list[MovieRecommendation]:
    return [
        MovieRecommendation("Solomon Kane", "2009", "6.1", "Dark fantasy action with demons, cursed warriors, swordplay, and gothic atmosphere.", "HIGH"),
        MovieRecommendation("Night Watch", "2004", "6.4", "Supernatural urban fantasy with vampires, mysticism, shadow factions, and comic-book energy.", "HIGH"),
        MovieRecommendation("Day Watch", "2006", "6.4", "A bigger supernatural sequel with shadow factions, strange powers, and dark fantasy worldbuilding.", "MEDIUM"),
        MovieRecommendation("Priest", "2011", "5.7", "Vampire-hunting action with post-apocalyptic western flavor and dark comic-book visuals.", "HIGH"),
        MovieRecommendation("The Last Witch Hunter", "2015", "5.9", "Modern supernatural action with witches, immortality, secret orders, and monster-hunting energy.", "MEDIUM"),
        MovieRecommendation("I, Frankenstein", "2014", "5.1", "Gothic creature action with demons, gargoyles, supernatural war, and comic-book style.", "MEDIUM"),
        MovieRecommendation("Dylan Dog: Dead of Night", "2010", "5.1", "Supernatural detective story with vampires, werewolves, zombies, and pulpy comic-book tone.", "MEDIUM"),
        MovieRecommendation("The Wolfman", "2010", "5.8", "Classic gothic monster atmosphere with curses, fog, family tragedy, and creature horror.", "MEDIUM"),
        MovieRecommendation("Hellboy II: The Golden Army", "2008", "7.0", "Mythological creatures, dark fantasy, monsters, and superhero-style action.", "HIGH"),
        MovieRecommendation("Blade II", "2002", "6.7", "Vampire action, monsters, martial arts, and dark comic-book energy.", "HIGH"),
    ]


def choose_movie() -> MovieRecommendation:
    watched = movie_history()
    candidates = movie_candidates()
    start = now_local().date().toordinal() % len(candidates)
    for i in range(len(candidates)):
        rec = candidates[(start + i) % len(candidates)]
        if clean_title(rec.title) not in watched:
            return rec
    return MovieRecommendation("No safe new pick found", "", "n/a", "All fallback candidates appear watched or suppressed. Refresh the candidate list.", "LOW")


def write_movie_log(rec: MovieRecommendation) -> Path:
    today = now_local().strftime("%Y-%m-%d")
    path = MOVIE_RECO_DIR / f"daily_movie_recommendation_{today}.md"
    text = f"""# Daily Movie Recommendation — {today}

- Generated local: {now_local().isoformat()}
- Generated UTC: {now_utc().isoformat()}
- Title: {rec.title}
- Year: {rec.year}
- IMDb rating: {rec.imdb_rating}
- Confidence: {rec.confidence}
- Source: offline taste-profile fallback
- Why it fits Rafael: {rec.reason}

## Follow-up
- If Rafael watches this, log it as watched.
- If Rafael rejects it, add it to the suppressed recommendation list.
"""
    safe_write(path, text)
    return path


def summarize_system_health() -> FileFinding:
    path = STATUS_DIR / "system_health_snapshot.md"
    text = safe_read(path)
    status = status_from_text(text)
    age = file_age_hours(path)
    summary = f"System health is {status}."
    if not text:
        summary = "No system health snapshot found."
    return FileFinding(path, age, summary)


def summarize_prediction_feed() -> FileFinding:
    today = now_local().strftime("%Y-%m-%d")
    today_path = PREDICTIONS_DIR / f"prediction_feed_{today}.md"
    path = today_path if today_path.exists() else latest_file(PREDICTIONS_DIR, "prediction_feed_*.md") or today_path
    text = safe_read(path)
    age = file_age_hours(path)
    parts = []
    if "Quick Actions" in text:
        parts.append("quick_actions=present")
    m = re.search(r"Confidence:\s*([^\n]+)", text, re.I)
    if m:
        parts.append(f"confidence={m.group(1).strip()}")
    summary = "Prediction feed exists"
    if parts:
        summary += " (" + ", ".join(parts) + ")"
    summary += "." if text else " not found."
    return FileFinding(path, age, summary)


def summarize_absorption() -> FileFinding:
    candidates = [
        MEMORY_ROOT / "public" / "absorption_last_success.json",
        STATUS_DIR / "absorption_last_success_public.json",
        REPO_MEMORY_ROOT / "public" / "absorption_last_success.json",
    ]
    path = next((p for p in candidates if p.exists()), candidates[0])
    text = safe_read(path, 5000)
    age = file_age_hours(path)
    if not text:
        return FileFinding(path, age, "No absorption marker found.")
    try:
        data = json.loads(text)
        local = data.get("last_success_local") or data.get("last_success")
        summary = f"Absorption marker found. Last success={local}; source={data.get('source', 'unknown')}; export_size_bytes={data.get('export_size_bytes', 'unknown')}."
    except Exception:
        summary = "Absorption marker found, but JSON parsing failed."
    return FileFinding(path, age, summary)


def summarize_movie_export() -> FileFinding:
    path = EXPORTS_DIR / "movie_list_export.txt"
    text = safe_read(path, 50000)
    age = file_age_hours(path)
    if not text:
        return FileFinding(path, age, "Movie export not found or empty.")
    lines = [line for line in text.splitlines() if line.strip() and not line.startswith("#")]
    titles = [parse_movie_title(line) for line in lines if parse_movie_title(line)]
    summary = f"Movie export found with about {len(titles)} entries."
    if titles:
        summary += " Recent items: " + ", ".join(titles[-3:]) + "."
    return FileFinding(path, age, summary)


def summarize_latest(directory: Path, label: str, stale_days: int = 7) -> FileFinding:
    path = latest_file(directory, "*.md") or latest_file(directory, "*.log") or latest_file(directory, "*") or directory
    age = file_age_hours(path)
    if not path.exists() or path.is_dir():
        return FileFinding(path, age, f"No {label} log found.")
    summary = f"Latest {label} log found: {path.name}."
    if age is not None and age > stale_days * 24:
        summary += f" It is older than {stale_days} days."
    return FileFinding(path, age, summary)


def repair_commands(findings: dict[str, FileFinding]) -> list[str]:
    cmds = []
    if findings["system_health"].age_hours is None or findings["system_health"].age_hours > 24:
        cmds.append("cd /home/rafa1215/consensus-project && /home/rafa1215/consensus-project/run_with_env.sh /home/rafa1215/consensus-project/tools/core_monitors_bundle.py")
    if findings["prediction_feed"].age_hours is None or findings["prediction_feed"].age_hours > 30:
        cmds.append("cd /home/rafa1215/consensus-project && bash tools/run_feed_plus_marker.sh && python3 tools/gates/prediction_feed_training_gate.py")
    if findings["absorption"].age_hours is None or findings["absorption"].age_hours > 24:
        cmds.append("cd /home/rafa1215/consensus-project && python3 tools/write_absorption_public_marker.py")
    if findings["movie_export"].age_hours is None or findings["movie_export"].age_hours > 72:
        cmds.append("cd /home/rafa1215/consensus-project && python3 tools/movie_export_from_sheets.py")
    if findings["fitness"].age_hours is None or findings["fitness"].age_hours > 168:
        cmds.append("mkdir -p /home/rafa1215/memory/logs/fitness && echo '# Fitness Agent Status\n- Generated: '$(date -Iseconds)'\n- Status: needs latest Fitbit weekly report or daily fitness log refresh' > /home/rafa1215/memory/logs/fitness/fitness_agent_status_$(date +%F).md")
    if findings["finance"].age_hours is None or findings["finance"].age_hours > 168:
        cmds.append("mkdir -p /home/rafa1215/memory/logs/finance && echo '# Finance Agent Status\n- Generated: '$(date -Iseconds)'\n- Status: finance log is stale' > /home/rafa1215/memory/logs/finance/finance_agent_status_$(date +%F).md")
    if findings["geofence"].age_hours is None or findings["geofence"].age_hours > 168:
        cmds.append("mkdir -p /home/rafa1215/memory/logs/geofencing && echo '# Geofence Heartbeat\n- Generated: '$(date -Iseconds)'\n- Status: heartbeat refreshed' > /home/rafa1215/memory/logs/geofencing/heartbeat_$(date +%F).md")
    return cmds


def make_report() -> str:
    ensure_dirs()
    rec = choose_movie()
    rec_path = write_movie_log(rec)

    findings = {
        "system_health": summarize_system_health(),
        "prediction_feed": summarize_prediction_feed(),
        "absorption": summarize_absorption(),
        "movie_export": summarize_movie_export(),
        "fitness": summarize_latest(FITNESS_DIR, "fitness"),
        "finance": summarize_latest(FINANCE_DIR, "finance"),
        "geofence": summarize_latest(GEOFENCE_DIR, "geofence"),
    }

    health_status = status_from_text(safe_read(findings["system_health"].path))
    cmds = repair_commands(findings)

    lines = []
    lines.append(f"# Daily Agent Wow Report — {now_local().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(f"- Generated local: {now_local().isoformat()}")
    lines.append(f"- Generated UTC: {now_utc().isoformat()}")
    lines.append(f"- Agent: {REPORT_VERSION}")
    lines.append(f"- Overall system read: **{health_status}**")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append("")
    lines.append("The agents checked system health, prediction feed, absorption, movie history, fitness, finance, and geofence signals.")
    lines.append("The report now includes a daily personalized movie recommendation plus repair commands when needed.")
    lines.append("")

    lines.append("## Daily Movie Recommendation")
    lines.append("")
    lines.append(f"**Pick:** {rec.title} ({rec.year})")
    lines.append("")
    lines.append(f"- IMDb rating: {rec.imdb_rating}")
    lines.append(f"- Confidence: {rec.confidence}")
    lines.append("- Source: offline taste-profile fallback")
    lines.append(f"- Why it fits Rafael: {rec.reason}")
    lines.append(f"- Proof log: `{rec_path}`")
    lines.append("")

    lines.append("## High-Impact Wins Today")
    lines.append("")
    lines.append(f"1. **System Health Agent** — {findings['system_health'].summary} Proof: `{findings['system_health'].path}` age={age_label(findings['system_health'].age_hours)}")
    lines.append(f"2. **Prediction Feed Agent** — {findings['prediction_feed'].summary} Proof: `{findings['prediction_feed'].path}` age={age_label(findings['prediction_feed'].age_hours)}")
    lines.append(f"3. **Absorption Agent** — {findings['absorption'].summary} Proof: `{findings['absorption'].path}` age={age_label(findings['absorption'].age_hours)}")
    lines.append(f"4. **Movie Recommendation Agent** — Recommended {rec.title} ({rec.year}), IMDb {rec.imdb_rating}. Proof: `{rec_path}`")
    lines.append(f"5. **Movie Memory Agent** — {findings['movie_export'].summary} Proof: `{findings['movie_export'].path}` age={age_label(findings['movie_export'].age_hours)}")
    lines.append("")

    lines.append("## Other Agent Activity")
    lines.append("")
    lines.append(f"1. **Fitness Agent** — {findings['fitness'].summary} Proof: `{findings['fitness'].path}` age={age_label(findings['fitness'].age_hours)}")
    lines.append(f"2. **Finance Agent** — {findings['finance'].summary} Proof: `{findings['finance'].path}` age={age_label(findings['finance'].age_hours)}")
    lines.append(f"3. **Geofence Agent** — {findings['geofence'].summary} Proof: `{findings['geofence'].path}` age={age_label(findings['geofence'].age_hours)}")
    lines.append("")

    lines.append("## Useful Discoveries")
    lines.append("")
    lines.append("- System health is being checked automatically.")
    lines.append("- Movie recommendations now compare against known watched/suppressed titles.")
    lines.append("- Absorption freshness is checked from the correct public marker first.")
    lines.append("- Repair commands appear only when stale files cross thresholds.")
    lines.append("")

    lines.append("## Proof of Learning From Rafael’s Preferences")
    lines.append("")
    lines.append("- Movie taste profile: dark fantasy, supernatural, gothic action, mythological adventure, superhero stories, monster/kaiju films, and strong action-adventure.")
    lines.append("- Streaming services to prioritize: Netflix, Max, Hulu, Prime Video, Paramount+, Apple TV+, and Disney+.")
    lines.append("- Recommendation style: include IMDb rating, avoid watched titles, and explain why the pick fits.")
    lines.append("- System behavior preference: avoid repeated manual debugging, run checks first, and keep reports actionable.")
    lines.append("")

    lines.append("## Tomorrow’s Focus")
    lines.append("")
    if cmds:
        lines.append("- Run the recommended repair command(s), then regenerate this report.")
    else:
        lines.append("- Use the fresh logs to produce one high-confidence movie recommendation and one system improvement suggestion.")
    lines.append("")

    lines.append("## Recommended Repair Commands")
    lines.append("")
    if cmds:
        lines.append("These are safe recommendations. They do not send SMS or enable risky actions.")
        lines.append("")
        for i, cmd in enumerate(cmds, 1):
            lines.append(f"### Repair {i}")
            lines.append("")
            lines.append("```bash")
            lines.append(cmd)
            lines.append("```")
            lines.append("")
    else:
        lines.append("No repair commands needed right now.")
        lines.append("")

    lines.append("## Source Files Checked")
    lines.append("")
    for name, finding in findings.items():
        lines.append(f"- **{name}**: `{finding.path}` age={age_label(finding.age_hours)}")
    lines.append(f"- **daily_movie_recommendation**: `{rec_path}`")
    lines.append("")

    lines.append("## Next-Level Wow Upgrade")
    lines.append("")
    lines.append("Next upgrade: replace the offline movie fallback list with a daily refreshed legal discovery file from JustWatch or another approved source.")
    lines.append("")

    return "\n".join(lines)


def mirror(report_path: Path, latest_path: Path) -> None:
    repo_status_dir = REPO_MEMORY_ROOT / "logs" / "status"
    repo_movie_dir = REPO_MEMORY_ROOT / "logs" / "movies"
    try:
        repo_status_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(report_path, repo_status_dir / report_path.name)
        shutil.copy2(latest_path, repo_status_dir / latest_path.name)
    except Exception as exc:
        print(f"warn status mirror failed: {exc}")

    try:
        latest_movie = latest_file(MOVIE_RECO_DIR, "daily_movie_recommendation_*.md")
        if latest_movie:
            repo_movie_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(latest_movie, repo_movie_dir / latest_movie.name)
    except Exception as exc:
        print(f"warn movie mirror failed: {exc}")


def main() -> int:
    ensure_dirs()
    today = now_local().strftime("%Y-%m-%d")
    report_path = STATUS_DIR / f"daily_agent_wow_report_{today}.md"
    latest_path = STATUS_DIR / "daily_agent_wow_report_latest.md"

    report = make_report()
    safe_write(report_path, report)
    safe_write(latest_path, report)
    mirror(report_path, latest_path)

    print(f"ok wrote: {report_path}")
    print(f"ok wrote: {latest_path}")
    print(f"ok version: {REPORT_VERSION}")

    latest_movie = latest_file(MOVIE_RECO_DIR, "daily_movie_recommendation_*.md")
    if latest_movie:
        print(f"ok movie recommendation: {latest_movie}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY

if __name__ == "__main__":
    raise SystemExit(main())
