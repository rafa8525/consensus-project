#!/usr/bin/env python3
"""
fitness_status_reporter.py

Summarizes the current state of fitness tracking logs for the AI Consensus System.

It:
- Scans memory/logs/fitness/ for any files
- Lists the most recent N files (default 10) with timestamps and sizes
- Writes a human-readable status report to:
    memory/logs/status/fitness_status_report.md

This is intentionally format-agnostic: it doesn't try to parse the internals
of the fitness logs, only shows recency and presence so you can quickly see if
logging is actually happening.
"""

import datetime
from datetime import timezone
from pathlib import Path
from typing import List, Tuple


# Hardcode project root for consistency with other tools
PROJECT_ROOT = Path("/home/rafa1215/consensus-project").resolve()
FITNESS_DIR = PROJECT_ROOT / "memory" / "logs" / "fitness"
STATUS_DIR = PROJECT_ROOT / "memory" / "logs" / "status"
STATUS_DIR.mkdir(parents=True, exist_ok=True)

REPORT_PATH = STATUS_DIR / "fitness_status_report.md"
MAX_FILES = 10  # how many recent files to list


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(timezone.utc)


def list_fitness_files() -> List[Path]:
    """Return all files under memory/logs/fitness (non-recursive)."""
    if not FITNESS_DIR.exists():
        return []
    return sorted(p for p in FITNESS_DIR.iterdir() if p.is_file())


def describe_file(p: Path) -> Tuple[str, float, int]:
    """
    Return (relative_path_str, age_hours, size_bytes)
    """
    rel = p.relative_to(PROJECT_ROOT)
    now_ts = utc_now().timestamp()
    mtime = p.stat().st_mtime
    age_hours = (now_ts - mtime) / 3600.0
    size_bytes = p.stat().st_size
    return str(rel), age_hours, size_bytes


def main() -> None:
    now = utc_now()
    date_str = now.date().isoformat()

    files = list_fitness_files()
    total_files = len(files)

    # Sort newest first by mtime
    files_sorted = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)
    recent_files = files_sorted[:MAX_FILES]

    lines: List[str] = []
    lines.append("Fitness Tracking Status Report")
    lines.append("")
    lines.append(f"Date (UTC): {date_str}")
    lines.append(f"Generated at (UTC): {now.isoformat()}")
    lines.append("")
    lines.append(f"Fitness log directory: `memory/logs/fitness/`")
    lines.append(f"Total files found: {total_files}")
    lines.append("")

    if total_files == 0:
        lines.append("## Status")
        lines.append("- No fitness log files were found.")
        lines.append("")
        lines.append("### Recommended Next Steps")
        lines.append("- Verify that fitness agents are writing to `memory/logs/fitness/`.")
        lines.append("- Confirm any scheduled tasks related to fitness tracking.")
        lines.append("- Run a manual fitness logging action (e.g., swim/steps/BMI entry) and re-run this tool.")
    else:
        lines.append("## Most Recent Fitness Log Files")
        lines.append(f"(Showing up to {MAX_FILES} newest files)")
        lines.append("")
        for p in recent_files:
            rel, age_hours, size_bytes = describe_file(p)
            age_str = f"{age_hours:.2f} hours"
            lines.append(f"- `{rel}`  —  age: {age_str}, size: {size_bytes} bytes")
        lines.append("")
        lines.append("## Interpretation")
        lines.append(
            "- Recent files indicate active logging if ages are small (e.g., <24 hours).\n"
            "- Older ages suggest gaps in logging or inactive fitness agents."
        )
        lines.append("")
        lines.append("### Recommended Next Steps")
        lines.append("- Ensure daily fitness logs continue to appear in this directory.")
        lines.append("- Consider adding separate scripts to parse and summarize steps/laps/BMI trends.")
        lines.append("- Optionally schedule this reporter weekly to keep an eye on recency.")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Fitness status report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
