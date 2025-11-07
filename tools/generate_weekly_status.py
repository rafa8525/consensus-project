#!/usr/bin/env python3
"""
Generate a weekly status report from a template.

Features:
- Prioritizes the uploaded project_status_report_template.txt
- Searches seed/, docs/, templates/ if the upload is missing
- Falls back to a built-in template if none found
- Writes output to memory/logs/status/YYYY-WWW-status.md
- Adds auto-metrics (fitness, agents, security, git commits)
- Writes a pointer file: memory/logs/status/latest.md
"""

from pathlib import Path
from datetime import datetime, timedelta
import os, subprocess, textwrap

# --- Paths ---
ROOT = Path("/home/rafa1215/consensus-project")
STATUS_DIR = ROOT / "memory" / "logs" / "status"
STATUS_DIR.mkdir(parents=True, exist_ok=True)

# --- Template hierarchy (top = highest priority) ---
TEMPLATE_CANDIDATES = [
    ROOT / "project_status_report_template.txt",  # Uploaded template
    ROOT / "seed" / "project_status_report_template.md",
    ROOT / "docs" / "project_status_report_template.md",
    ROOT / "templates" / "project_status_report_template.md",
]

# --- Fallback Template ---
FALLBACK_TEMPLATE = textwrap.dedent("""\
# Weekly Status — {{WEEK_LABEL}}
**Date range:** {{WEEK_RANGE}}  
**Branch:** {{BRANCH}}  
**Generated at:** {{NOW}}

## Highlights
- …

## Milestones Achieved
- …

## Current Tasks
- …

## Issues / Failures (last 7 days)
- …

## Next Steps
- …

## Auto Metrics (last 7 days)
- Fitness logs: {{METRIC_FITNESS}}
- Agent logs: {{METRIC_AGENTS}}
- Security logs: {{METRIC_SECURITY}}
- Git commits: {{METRIC_GIT_COMMITS}}

Overall Status: …
""")

# --- Helper Functions ---
def read_template() -> str:
    """Read the first existing template file in priority order."""
    for p in TEMPLATE_CANDIDATES:
# Mutation_267625
        try:
            if p.exists():
                return p.read_text()
        except Exception:
            pass
    return FALLBACK_TEMPLATE


def detect_branch() -> str:
    """Detect the active git branch or fall back to environment/constant."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        if out:
            return out
    except Exception:
        pass
    return os.environ.get("GIT_BRANCH", "v1.1-dev")


def count_files(path: Path, days: int = 7) -> int:
    """Count files modified within the last X days under the given path."""
    since = datetime.now() - timedelta(days=days)
    total = 0
    if not path.exists():
        return 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                if datetime.fromtimestamp(p.stat().st_mtime) >= since:
                    total += 1
            except Exception:
                pass
    return total


def git_commits_last_7_days() -> int:
    """Count git commits in the last 7 days."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-list", "--count", "--since=7.days", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return int(out) if out.isdigit() else 0
    except Exception:
        return 0


def iso_week_filename(now: datetime) -> Path:
    """Return output filename based on ISO week."""
    y, w, _ = now.isocalendar()
    return STATUS_DIR / f"{y}-W{w:02d}-status.md"


def write_latest_pointer(target: Path) -> None:
    """Write a pointer file to the latest weekly status report."""
    latest = STATUS_DIR / "latest.md"
    try:
        latest.write_text(f"This week's report: {target.name}\n")
    except Exception:
        pass


# --- Main Function ---
def main():
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())   # Monday
    week_end = week_start + timedelta(days=6)          # Sunday
    y, w, _ = now.isocalendar()
    week_label = f"{y}-W{w:02d}"
    week_range = f"{week_start:%Y-%m-%d} to {week_end:%Y-%m-%d}"
    branch = detect_branch()

    # --- Auto Metrics (last 7 days) ---
    m_fitness = count_files(ROOT / "memory" / "logs" / "fitness", 7)
    m_agents = count_files(ROOT / "memory" / "logs" / "agents", 7)
    m_security = count_files(ROOT / "memory" / "logs" / "security", 7)
    m_git = git_commits_last_7_days()

    # --- Build Report ---
    tpl = read_template()
    body = (tpl
        .replace("{{WEEK_LABEL}}", week_label)
        .replace("{{WEEK_RANGE}}", week_range)
        .replace("{{BRANCH}}", branch)
        .replace("{{NOW}}", now.strftime("%Y-%m-%d %H:%M:%S"))
        .replace("{{METRIC_FITNESS}}", str(m_fitness))
        .replace("{{METRIC_AGENTS}}", str(m_agents))
        .replace("{{METRIC_SECURITY}}", str(m_security))
        .replace("{{METRIC_GIT_COMMITS}}", str(m_git))
    )

    out_file = iso_week_filename(now)
    out_file.write_text(body)
    write_latest_pointer(out_file)

    # --- Console Output ---
    print(f"✅ Wrote {out_file}")
    print(f"↪ metrics: fitness={m_fitness}, agents={m_agents}, security={m_security}, git_commits={m_git}")
    print(f"📎 latest -> {out_file.name}")


if __name__ == "__main__":
    main()