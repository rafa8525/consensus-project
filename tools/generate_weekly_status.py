#!/usr/bin/env python3
"""
Generate a weekly status report from a template.
- Searches seed/, docs/, templates/ for project_status_report_template.md (in that order).
- Falls back to a built-in template.
- Writes to memory/logs/status/YYYY-WWW-status.md (ISO week with 'W').
- Adds last-7-day auto-metrics (fitness/agents/security/git commits).
- Writes a text pointer: memory/logs/status/latest.md
"""
from pathlib import Path
from datetime import datetime, timedelta
import os, subprocess, textwrap

ROOT = Path("/home/rafa1215/consensus-project")
STATUS_DIR = ROOT / "memory" / "logs" / "status"
STATUS_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATE_CANDIDATES = [
    ROOT / "seed" / "project_status_report_template.md",
    ROOT / "docs" / "project_status_report_template.md",
    ROOT / "templates" / "project_status_report_template.md",
]

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

def read_template() -> str:
    for p in TEMPLATE_CANDIDATES:
        try:
            if p.exists():
                return p.read_text()
        except Exception:
            pass
    return FALLBACK_TEMPLATE

def detect_branch() -> str:
    # Prefer git; fall back to env; finally 'v1.1-dev'
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
    since = datetime.now() - timedelta(days=days)
    total = 0
    try:
        for p in path.rglob("*"):
            if p.is_file():
                try:
                    if datetime.fromtimestamp(p.stat().st_mtime) >= since:
                        total += 1
                except Exception:
                    pass
    except Exception:
        pass
    return total

def git_commits_last_7_days() -> int:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-list", "--count", "--since=7.days", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return int(out) if out.isdigit() else 0
    except Exception:
        return 0

def iso_week_filename(now: datetime):
    y, w, _ = now.isocalendar()
    return STATUS_DIR / f"{y}-W{w:02d}-status.md"

def write_latest_pointer(target: Path) -> None:
    latest = STATUS_DIR / "latest.md"
    try:
        latest.write_text(f"This week's report: {target.name}\n")
    except Exception:
        pass

def main():
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())   # Monday
    week_end   = week_start + timedelta(days=6)        # Sunday
    y, w, _ = now.isocalendar()
    week_label = f"{y}-W{w:02d}"
    week_range = f"{week_start:%Y-%m-%d} to {week_end:%Y-%m-%d}"
    branch = detect_branch()

    # Auto-metrics (last 7 days)
    m_fitness  = count_files(ROOT / "memory" / "logs" / "fitness", 7)
    m_agents   = count_files(ROOT / "memory" / "logs" / "agents", 7)
    m_security = count_files(ROOT / "memory" / "logs" / "security", 7)
    m_git      = git_commits_last_7_days()

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

    print(f"✅ Wrote {out_file}")
    print(f"↪ metrics: fitness={{m_fitness}}, agents={{m_agents}}, security={{m_security}}, git_commits={{m_git}}")
    print(f"📎 latest -> {out_file.name}")

if __name__ == "__main__":
    main()
