#!/usr/bin/env python3
"""
daily_impress_rafael_agent.py

Daily proof-based "Impress Rafael" report for the AI Consensus System.

Safe behavior:
- No paid APIs.
- No SMS sending.
- No voice calls.
- No destructive actions.
- Writes Markdown/JSON proof reports only.
- Uses existing local tools when --self-heal is enabled.

What it checks:
1. System health snapshot freshness.
2. Prediction feed freshness and content.
3. Same-day fitness log.
4. Movie monitor freshness.
5. Memory absorption marker freshness.
6. Security/VPN audit posture.
7. Agent-area scoreboard.
8. Best next actions.

Output:
- /home/rafa1215/memory/logs/system/impress_reports/impress_rafael_YYYY-MM-DD.md
- /home/rafa1215/memory/logs/system/impress_reports/impress_rafael_YYYY-MM-DD.json
- /home/rafa1215/memory/logs/system/impress_reports/latest.md
- /home/rafa1215/memory/logs/system/impress_reports/latest.json
- mirrored markdown under repo memory tree
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_REPO_ROOT = Path("/home/rafa1215/consensus-project")
DEFAULT_MEM_ROOT = Path("/home/rafa1215/memory")

REPORT_SUBDIR = Path("logs/system/impress_reports")
STATUS_SUBDIR = Path("logs/status")

MAX_COMMAND_SECONDS = 90


@dataclass
class CheckResult:
    name: str
    status: str
    score: int
    detail: str
    evidence_path: str | None = None


@dataclass
class CommandResult:
    command: str
    returncode: int
    stdout_tail: str
    stderr_tail: str


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def today_str() -> str:
    return now_utc().strftime("%Y-%m-%d")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def tail(text: str, chars: int = 4000) -> str:
    if len(text) <= chars:
        return text
    return text[-chars:]


def read_text(path: Path, limit_chars: int = 25000) -> str:
    try:
        if not path.exists():
            return ""
        text = path.read_text(errors="replace")
        if len(text) > limit_chars:
            return text[-limit_chars:]
        return text
    except Exception as exc:
        return f"[read_error] {type(exc).__name__}: {exc}"


def read_json(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        return json.loads(path.read_text(errors="replace"))
    except Exception:
        return {}


def file_age_hours(path: Path) -> float | None:
    try:
        if not path.exists():
            return None
        mtime = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        return (now_utc() - mtime).total_seconds() / 3600
    except Exception:
        return None


def newest_file_under(path: Path) -> Path | None:
    if not path.exists():
        return None

    if path.is_file():
        return path

    newest: Path | None = None
    newest_mtime = -1.0

    try:
        for candidate in path.rglob("*"):
            if not candidate.is_file():
                continue
            try:
                mtime = candidate.stat().st_mtime
            except OSError:
                continue
            if mtime > newest_mtime:
                newest = candidate
                newest_mtime = mtime
    except Exception:
        return None

    return newest


def run_command(repo_root: Path, command: list[str], timeout: int = MAX_COMMAND_SECONDS) -> CommandResult:
    command_display = " ".join(command)

    try:
        proc = subprocess.run(
            command,
            cwd=str(repo_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return CommandResult(
            command=command_display,
            returncode=proc.returncode,
            stdout_tail=tail(proc.stdout, 2500),
            stderr_tail=tail(proc.stderr, 2500),
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return CommandResult(
            command=command_display,
            returncode=124,
            stdout_tail=tail(stdout, 2500),
            stderr_tail=tail(stderr + f"\nTimed out after {timeout} seconds", 2500),
        )
    except Exception as exc:
        return CommandResult(
            command=command_display,
            returncode=1,
            stdout_tail="",
            stderr_tail=f"{type(exc).__name__}: {exc}",
        )


def command_exists(repo_root: Path, relative_path: str) -> bool:
    return (repo_root / relative_path).exists()


def run_self_heal(repo_root: Path) -> list[CommandResult]:
    """
    Runs safe local refresh commands.

    This intentionally avoids SMS/voice and only runs project-local maintenance tools.
    Missing optional tools are skipped.
    """

    planned: list[list[str]] = []

    if command_exists(repo_root, "tools/verify_knowledge_base.py"):
        planned.append(["python3", "tools/verify_knowledge_base.py"])

    if command_exists(repo_root, "tools/movies_monitor.py"):
        planned.append(["python3", "tools/movies_monitor.py"])

    if command_exists(repo_root, "tools/security_vpn_audit.py"):
        planned.append(["python3", "tools/security_vpn_audit.py"])

    if command_exists(repo_root, "tools/core_monitors_bundle.py"):
        planned.append(["python3", "tools/core_monitors_bundle.py"])

    if command_exists(repo_root, "agents/prediction_feed_agent.py"):
        planned.append(["python3", "agents/prediction_feed_agent.py"])

    results: list[CommandResult] = []
    for command in planned:
        results.append(run_command(repo_root, command))

    return results


def parse_overall_health(snapshot_text: str) -> str:
    match = re.search(r"Overall:\s*([A-Za-z0-9_\- ]+)", snapshot_text)
    if match:
        return match.group(1).strip().lower()

    if "| Subsystem | Status | Notes |" in snapshot_text:
        if re.search(r"\|\s*(fail|error|stale|warning)\s*\|", snapshot_text, re.IGNORECASE):
            return "warning"
        return "ok"

    return "unknown"


def check_system_health(mem_root: Path) -> CheckResult:
    path = mem_root / STATUS_SUBDIR / "system_health_snapshot.md"
    text = read_text(path)
    age = file_age_hours(path)

    if not text:
        return CheckResult(
            name="System health snapshot",
            status="fail",
            score=0,
            detail="Missing system_health_snapshot.md.",
            evidence_path=str(path),
        )

    overall = parse_overall_health(text)

    if age is None:
        return CheckResult(
            name="System health snapshot",
            status="warning",
            score=40,
            detail=f"Snapshot exists but age could not be determined. Overall parsed status: {overall}.",
            evidence_path=str(path),
        )

    if age > 24:
        return CheckResult(
            name="System health snapshot",
            status="stale",
            score=35,
            detail=f"Snapshot is stale at {age:.1f} hours old. Overall parsed status: {overall}.",
            evidence_path=str(path),
        )

    if overall == "ok":
        return CheckResult(
            name="System health snapshot",
            status="ok",
            score=100,
            detail=f"Snapshot is fresh at {age:.1f} hours old and reports overall ok.",
            evidence_path=str(path),
        )

    return CheckResult(
        name="System health snapshot",
        status="warning",
        score=65,
        detail=f"Snapshot is fresh at {age:.1f} hours old but overall status is {overall}.",
        evidence_path=str(path),
    )


def check_prediction_feed(mem_root: Path) -> CheckResult:
    date = today_str()
    path = mem_root / "logs/system/predictions" / f"prediction_feed_{date}.md"
    text = read_text(path)
    age = file_age_hours(path)

    if not text:
        return CheckResult(
            name="Prediction feed",
            status="missing",
            score=10,
            detail=f"Today's prediction feed is missing for {date}.",
            evidence_path=str(path),
        )

    has_health_line = "System health snapshot" in text
    has_fitness_line = "Health/Fitness" in text or "Fitness" in text
    has_entertainment = (
        "Movie" in text
        or "Streaming" in text
        or "Recommendation" in text
        or "Tonight" in text
    )
    has_stale_warning = (
        "ACTION REQUIRED: STALE" in text
        or "System health snapshot: STALE" in text
        or "STALE" in text
    )

    score = 50
    reasons: list[str] = []

    if age is not None and age <= 24:
        score += 20
        reasons.append(f"fresh at {age:.1f} hours old")
    else:
        reasons.append("not fresh or age unknown")

    if has_health_line:
        score += 10
        reasons.append("contains system health reference")

    if has_fitness_line:
        score += 10
        reasons.append("contains fitness signal")

    if has_entertainment:
        score += 10
        reasons.append("contains entertainment signal")

    if has_stale_warning:
        score -= 20
        reasons.append("contains stale/action-required warning")

    score = max(0, min(100, score))
    status = "ok" if score >= 80 else "warning"

    return CheckResult(
        name="Prediction feed",
        status=status,
        score=score,
        detail=", ".join(reasons),
        evidence_path=str(path),
    )


def check_fitness_log(mem_root: Path) -> CheckResult:
    date = today_str()
    path = mem_root / "logs/fitness" / f"daily_{date}.md"
    text = read_text(path)
    age = file_age_hours(path)

    if not text:
        return CheckResult(
            name="Fitness activity log",
            status="missing",
            score=25,
            detail=f"No same-day fitness log found for {date}.",
            evidence_path=str(path),
        )

    lower = text.lower()
    has_steps = bool(re.search(r"steps\s*[:=]\s*\d+", lower)) or "steps" in lower
    has_laps = "laps" in lower or "swim" in lower
    has_note = "note" in lower or len(text.strip()) > 20

    score = 65
    details: list[str] = []

    if age is not None:
        details.append(f"log age {age:.1f} hours")
        if age <= 24:
            score += 10

    if has_steps:
        score += 15
        details.append("step signal present")

    if has_laps:
        score += 15
        details.append("swim/laps signal present")

    if has_note:
        score += 5
        details.append("note/detail present")

    score = max(0, min(100, score))

    return CheckResult(
        name="Fitness activity log",
        status="ok" if score >= 80 else "partial",
        score=score,
        detail=", ".join(details) if details else "Fitness log exists.",
        evidence_path=str(path),
    )


def check_movies_monitor(mem_root: Path) -> CheckResult:
    path = mem_root / "logs/system/movies_monitor_status.json"
    data = read_json(path)
    age = file_age_hours(path)

    if not data:
        return CheckResult(
            name="Movie monitor",
            status="missing",
            score=20,
            detail="Movie monitor status JSON is missing or unreadable.",
            evidence_path=str(path),
        )

    last_result = str(data.get("last_result", data.get("status", "unknown"))).lower()
    last_error = str(data.get("last_error", "")).strip()

    score = 60
    details: list[str] = []

    if age is not None and age <= 24:
        score += 25
        details.append(f"fresh at {age:.1f} hours old")
    elif age is not None:
        score -= 20
        details.append(f"stale at {age:.1f} hours old")
    else:
        details.append("age unknown")

    if last_result in {"success", "ok", "no_new_movies", "no new movies"}:
        score += 15
        details.append(f"last result {last_result}")
    elif last_error:
        score -= 20
        details.append(f"last error: {last_error[:160]}")
    else:
        details.append(f"last result {last_result}")

    new_titles = data.get("new_titles") or data.get("seen_titles") or []
    if isinstance(new_titles, list) and new_titles:
        score += 5
        details.append(f"title signal present ({len(new_titles)})")

    score = max(0, min(100, score))

    return CheckResult(
        name="Movie monitor",
        status="ok" if score >= 80 else "warning",
        score=score,
        detail=", ".join(details),
        evidence_path=str(path),
    )


def check_absorption_marker(mem_root: Path) -> CheckResult:
    candidates = [
        mem_root / "public/absorption_last_success.json",
        mem_root / "logs/status/absorption_last_success_public.json",
    ]

    existing = [p for p in candidates if p.exists()]
    if not existing:
        return CheckResult(
            name="Memory absorption marker",
            status="missing",
            score=15,
            detail="No public absorption marker found.",
            evidence_path=str(candidates[0]),
        )

    path = existing[0]
    data = read_json(path)
    age = file_age_hours(path)

    score = 55
    details: list[str] = []

    if age is not None and age <= 24:
        score += 35
        details.append(f"fresh at {age:.1f} hours old")
    elif age is not None:
        score -= 20
        details.append(f"stale at {age:.1f} hours old")
    else:
        details.append("age unknown")

    success_metadata = (
        data.get("source")
        or data.get("last_success_local")
        or data.get("last_success_utc")
        or data.get("marker_write_iso_utc")
    )

    if success_metadata:
        score += 10
        details.append("marker contains success metadata")

    score = max(0, min(100, score))

    return CheckResult(
        name="Memory absorption marker",
        status="ok" if score >= 80 else "warning",
        score=score,
        detail=", ".join(details),
        evidence_path=str(path),
    )


def check_security_audit(mem_root: Path, repo_root: Path) -> CheckResult:
    """
    Prefer fresh proof generated by tools/security_vpn_audit.py.
    Fall back to older schedule files if no audit proof exists.
    """

    preferred_files = [
        mem_root / "logs/security/security_vpn_audit_latest.md",
        mem_root / "logs/security/security_vpn_audit_latest.json",
        repo_root / "memory/logs/security/security_vpn_audit_latest.md",
        repo_root / "memory/logs/security/security_vpn_audit_latest.json",
    ]

    for path in preferred_files:
        if not path.exists():
            continue

        age = file_age_hours(path)
        text = read_text(path) if path.suffix == ".md" else ""
        data = read_json(path) if path.suffix == ".json" else {}

        score_from_file = None
        if data:
            try:
                score_from_file = int(data.get("score"))
            except Exception:
                score_from_file = None

        if score_from_file is None and text:
            match = re.search(r"Score:\s*(\d+)\s*/\s*100", text)
            if match:
                score_from_file = int(match.group(1))

        base_score = score_from_file if score_from_file is not None else 80
        details: list[str] = []

        if age is not None and age <= 31 * 24:
            details.append(f"fresh audit proof at {age / 24:.1f} days old")
        elif age is not None:
            base_score -= 25
            details.append(f"audit proof stale at {age / 24:.1f} days old")
        else:
            base_score -= 10
            details.append("audit proof age unknown")

        base_score = max(0, min(100, base_score))

        return CheckResult(
            name="Security audit posture",
            status="ok" if base_score >= 80 else "warning",
            score=base_score,
            detail=", ".join(details),
            evidence_path=str(path),
        )

    fallback_paths = [
        mem_root / "logs/security",
        repo_root / "memory/logs/security",
        repo_root / "security_audit_schedule.txt",
        repo_root / "vpn_activation_feature.txt",
        repo_root / "vpn_activation_testing_plan.txt",
        repo_root / "VPNActivationTestingPlan.txt",
    ]

    existing = [p for p in fallback_paths if p.exists()]
    if not existing:
        return CheckResult(
            name="Security audit posture",
            status="warning",
            score=45,
            detail="No security/VPN audit proof or schedule files found in expected paths.",
            evidence_path=None,
        )

    newest: Path | None = None
    newest_age: float | None = None

    for item in existing:
        candidate = newest_file_under(item)
        if not candidate:
            continue
        age = file_age_hours(candidate)
        if age is not None and (newest_age is None or age < newest_age):
            newest = candidate
            newest_age = age

    if newest_age is None:
        return CheckResult(
            name="Security audit posture",
            status="partial",
            score=60,
            detail="Security/VPN evidence exists, but no file freshness could be calculated.",
            evidence_path=str(existing[0]),
        )

    if newest_age <= 31 * 24:
        return CheckResult(
            name="Security audit posture",
            status="ok",
            score=85,
            detail=f"Security/VPN evidence exists. Newest item is {newest_age / 24:.1f} days old.",
            evidence_path=str(newest),
        )

    return CheckResult(
        name="Security audit posture",
        status="stale",
        score=50,
        detail=f"Security/VPN evidence exists but newest item is {newest_age / 24:.1f} days old. Run tools/security_vpn_audit.py.",
        evidence_path=str(newest),
    )


def weighted_score(checks: list[CheckResult], names: list[str], default: int = 50) -> int:
    matches = [check.score for check in checks if check.name in names]
    if not matches:
        return default
    return int(round(sum(matches) / len(matches)))


def grade(score: int) -> str:
    if score >= 95:
        return "A+"
    if score >= 90:
        return "A"
    if score >= 85:
        return "B+"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "Needs repair"


def create_scoreboard(checks: list[CheckResult]) -> list[dict[str, Any]]:
    areas = [
        {
            "agent_area": "Monitoring Regression Prevention Agent",
            "score": weighted_score(
                checks,
                ["System health snapshot", "Memory absorption marker"],
                default=60,
            ),
            "mission": "Keep core health fresh and self-heal stale feeder files.",
        },
        {
            "agent_area": "Prediction Feed Agent",
            "score": weighted_score(checks, ["Prediction feed"], default=50),
            "mission": "Generate useful daily recommendations and warnings.",
        },
        {
            "agent_area": "Fitness Tracking Agent",
            "score": weighted_score(checks, ["Fitness activity log"], default=50),
            "mission": "Track daily activity, Fitbit trends, sleep, and swim/step progress.",
        },
        {
            "agent_area": "Movie Recommendation Agent",
            "score": weighted_score(checks, ["Movie monitor", "Prediction feed"], default=50),
            "mission": "Find fresh streaming picks that match Rafael's taste and avoid repeats.",
        },
        {
            "agent_area": "Security and VPN Agent",
            "score": weighted_score(checks, ["Security audit posture"], default=50),
            "mission": "Maintain privacy, VPN readiness, and monthly audit discipline.",
        },
    ]

    areas.sort(key=lambda item: item["score"], reverse=True)

    for index, area in enumerate(areas, start=1):
        area["rank"] = index
        area["grade"] = grade(int(area["score"]))

    return areas


def overall_score(checks: list[CheckResult]) -> int:
    if not checks:
        return 0
    return int(round(sum(check.score for check in checks) / len(checks)))


def best_next_actions(checks: list[CheckResult]) -> list[str]:
    actions: list[str] = []
    by_name = {check.name: check for check in checks}

    health = by_name.get("System health snapshot")
    if health and health.score < 80:
        actions.append(
            "Run monitor self-heal: verify knowledge base, refresh movie monitor, rebuild system health, rerun prediction feed."
        )

    feed = by_name.get("Prediction feed")
    if feed and feed.score < 80:
        actions.append(
            "Improve today's prediction feed so it includes health, fitness, and one personalized entertainment recommendation."
        )

    fitness = by_name.get("Fitness activity log")
    if fitness and fitness.score < 80:
        actions.append(
            "Add today's fitness signal using tools/quick_log.py or the latest Fitbit data."
        )

    movie = by_name.get("Movie monitor")
    if movie and movie.score < 80:
        actions.append(
            "Refresh movie monitor and verify tools/movies_monitor.py rewrites movies_monitor_status.json even when no new movies are found."
        )

    absorption = by_name.get("Memory absorption marker")
    if absorption and absorption.score < 80:
        actions.append(
            "Refresh the absorption marker so Voice and text sessions can see recent memory sync status."
        )

    security = by_name.get("Security audit posture")
    if security and security.score < 80:
        actions.append(
            "Run tools/security_vpn_audit.py and confirm VPN/public-Wi-Fi audit proof is fresh."
        )

    if not actions:
        actions.append(
            "Shift from repair mode to wow mode: deliver one proactive recommendation, one system improvement, and one useful warning tomorrow."
        )

    return actions[:5]


def markdown_escape_table(value: str) -> str:
    return value.replace("\n", "<br>").replace("|", "\\|").strip()


def build_markdown(
    checks: list[CheckResult],
    scoreboard: list[dict[str, Any]],
    actions: list[str],
    self_heal_results: list[CommandResult],
) -> str:
    score = overall_score(checks)
    generated = now_utc().isoformat()

    if score >= 95:
        verdict = "Excellent. The agents are operating in wow mode."
    elif score >= 90:
        verdict = "Very good. The agents are close to wow mode, with only minor polish needed."
    elif score >= 80:
        verdict = "Good. The agents are functioning well, with room for sharper proactive output."
    elif score >= 70:
        verdict = "Mixed. The system is useful but still needs self-healing or freshness improvements."
    else:
        verdict = "Needs attention. The agents are not yet delivering the expected daily proof of value."

    lines: list[str] = []
    lines.append(f"# Daily Impress Rafael Report - {today_str()}")
    lines.append("")
    lines.append(f"Generated UTC: {generated}")
    lines.append("")
    lines.append(f"Overall score: {score}/100")
    lines.append("")
    lines.append(f"Verdict: {verdict}")
    lines.append("")
    lines.append("## What the agents proved today")
    lines.append("")
    lines.append("| Area | Status | Score | Evidence | Detail |")
    lines.append("|---|---:|---:|---|---|")

    for check in checks:
        evidence = check.evidence_path or "n/a"
        detail = markdown_escape_table(check.detail)
        lines.append(
            f"| {check.name} | {check.status} | {check.score} | `{evidence}` | {detail} |"
        )

    lines.append("")
    lines.append("## Agent performance scoreboard")
    lines.append("")
    lines.append("| Rank | Agent area | Grade | Score | Mission |")
    lines.append("|---:|---|---:|---:|---|")

    for item in scoreboard:
        lines.append(
            f"| {item['rank']} | {item['agent_area']} | {item['grade']} | {item['score']} | {item['mission']} |"
        )

    lines.append("")
    lines.append("## Best next actions")
    lines.append("")

    for index, action in enumerate(actions, start=1):
        lines.append(f"{index}. {action}")

    if self_heal_results:
        lines.append("")
        lines.append("## Self-heal command proof")
        lines.append("")
        lines.append("| Command | Exit | Stdout tail | Stderr tail |")
        lines.append("|---|---:|---|---|")

        for result in self_heal_results:
            stdout_clean = markdown_escape_table(result.stdout_tail) or "n/a"
            stderr_clean = markdown_escape_table(result.stderr_tail) or "n/a"
            lines.append(
                f"| `{result.command}` | {result.returncode} | {stdout_clean} | {stderr_clean} |"
            )

    lines.append("")
    lines.append("## Wow-mode expectation for tomorrow")
    lines.append("")
    lines.append(
        "The agents should deliver one clear useful result without Rafael needing to ask: "
        "a fresh system-health proof, one personalized recommendation, and one proactive improvement."
    )
    lines.append("")

    return "\n".join(lines)


def write_reports(
    mem_root: Path,
    repo_root: Path,
    markdown: str,
    payload: dict[str, Any],
) -> tuple[Path, Path, Path]:
    date = today_str()

    canonical_dir = mem_root / REPORT_SUBDIR
    repo_dir = repo_root / "memory" / REPORT_SUBDIR

    ensure_dir(canonical_dir)
    ensure_dir(repo_dir)

    md_path = canonical_dir / f"impress_rafael_{date}.md"
    json_path = canonical_dir / f"impress_rafael_{date}.json"
    repo_md_path = repo_dir / f"impress_rafael_{date}.md"

    latest_md = canonical_dir / "latest.md"
    latest_json = canonical_dir / "latest.json"

    md_path.write_text(markdown)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    latest_md.write_text(markdown)
    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True))

    shutil.copy2(md_path, repo_md_path)

    repo_latest_md = repo_dir / "latest.md"
    shutil.copy2(latest_md, repo_latest_md)

    return md_path, json_path, repo_md_path


def build_payload(
    checks: list[CheckResult],
    scoreboard: list[dict[str, Any]],
    actions: list[str],
    self_heal_results: list[CommandResult],
) -> dict[str, Any]:
    return {
        "generated_utc": now_utc().isoformat(),
        "date": today_str(),
        "overall_score": overall_score(checks),
        "checks": [asdict(check) for check in checks],
        "scoreboard": scoreboard,
        "best_next_actions": actions,
        "self_heal_results": [asdict(result) for result in self_heal_results],
    }


def run_checks(mem_root: Path, repo_root: Path) -> list[CheckResult]:
    return [
        check_system_health(mem_root),
        check_prediction_feed(mem_root),
        check_fitness_log(mem_root),
        check_movies_monitor(mem_root),
        check_absorption_marker(mem_root),
        check_security_audit(mem_root, repo_root),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Rafael's daily AI agent proof/impress report."
    )
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    parser.add_argument("--mem-root", default=str(DEFAULT_MEM_ROOT))
    parser.add_argument("--self-heal", action="store_true")
    parser.add_argument("--no-self-heal", action="store_true")
    parser.add_argument(
        "--always-self-heal",
        action="store_true",
        help="Run safe refresh commands before checks even if current health looks okay.",
    )

    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    mem_root = Path(args.mem_root)

    if not repo_root.exists():
        print(f"ERROR: repo root missing: {repo_root}", file=sys.stderr)
        return 2

    if not mem_root.exists():
        print(f"ERROR: memory root missing: {mem_root}", file=sys.stderr)
        return 2

    self_heal_results: list[CommandResult] = []

    pre_checks = run_checks(mem_root, repo_root)
    pre_score = overall_score(pre_checks)

    should_self_heal = (
        not args.no_self_heal
        and (
            args.always_self_heal
            or args.self_heal
            and any(check.score < 80 for check in pre_checks)
        )
    )

    if should_self_heal:
        self_heal_results = run_self_heal(repo_root)

    checks = run_checks(mem_root, repo_root)
    scoreboard = create_scoreboard(checks)
    actions = best_next_actions(checks)

    payload = build_payload(checks, scoreboard, actions, self_heal_results)
    payload["pre_self_heal_score"] = pre_score
    payload["self_heal_ran"] = bool(self_heal_results)

    markdown = build_markdown(checks, scoreboard, actions, self_heal_results)
    md_path, json_path, repo_md_path = write_reports(mem_root, repo_root, markdown, payload)

    print(f"OK: wrote canonical markdown: {md_path}")
    print(f"OK: wrote canonical json: {json_path}")
    print(f"OK: mirrored markdown: {repo_md_path}")
    print(f"Overall score: {payload['overall_score']}/100")

    if payload["overall_score"] < 70:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())