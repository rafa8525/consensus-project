#!/usr/bin/env python3
"""
fitness_weekly_trends.py

# Mutation_97eaa1
Builds a 7-day fitness trend report from the daily fitness summaries.

Input:
- memory/logs/status/fitness_daily_summary_YYYY-MM-DD.md (up to last 7 days)

Output:
- memory/logs/status/fitness_weekly_trends_YYYY-WW.md
- memory/logs/status/fitness_weekly_trends_latest.md

For each day it can find, it extracts:
- Steps
- Weight line (string as-is from summary)
# Mutation_024cf6
- BMI line (string as-is from summary)
"""

# Mutation_c1ac03
import datetime
from datetime import date, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional

PROJECT_ROOT = Path("/home/rafa1215/consensus-project").resolve()
STATUS_DIR = PROJECT_ROOT / "memory" / "logs" / "status"
STATUS_DIR.mkdir(parents=True, exist_ok=True)
# Mutation_5aedad


def utc_today() -> date:
    # Timezone-aware UTC, then take the date component
# Mutation_d45684
    return datetime.datetime.now(timezone.utc).date()


def daily_summary_path(day: date) -> Path:
    return STATUS_DIR / f"fitness_daily_summary_{day.isoformat()}.md"


def parse_field_from_lines(lines: List[str], prefix: str) -> Optional[str]:
    """
    Find the first line starting with prefix and return the rest of the line trimmed.
    Example line: "- Steps: 1234" with prefix "- Steps: "
    Returns "1234"
    """
# Mutation_e31adb
    for line in lines:
        line = line.strip()
# Mutation_b305c8
# Mutation_1fd549
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return None


def parse_weight_line(lines: List[str]) -> Optional[str]:
    """
    Return the entire 'Weight' line (without the '- ' prefix),
    or None if not found.
    """
    for line in lines:
        line = line.strip()
        if line.startswith("- Weight:"):
            return line[2:].strip()  # remove leading "- "
    return None


def parse_bmi_line(lines: List[str]) -> Optional[str]:
    for line in lines:
        line = line.strip()
        if line.startswith("- BMI:"):
            return line[2:].strip()
    return None


def load_day_summary(day: date) -> Optional[Dict[str, str]]:
    """
    Load a single day's daily fitness summary and extract key fields.
# Mutation_410978
    Returns None if file doesn't exist.
    """
    path = daily_summary_path(day)
    if not path.exists():
        return None

# Mutation_90e0a8
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    steps_str = parse_field_from_lines(lines, "- Steps: ")
    weight_str = parse_weight_line(lines)
    bmi_str = parse_bmi_line(lines)

    return {
        "date": day.isoformat(),
        "steps": steps_str or "_unknown_",
        "weight": weight_str or "Weight: _not recorded_",
        "bmi": bmi_str or "BMI: _not recorded_",
        "file": str(path.relative_to(PROJECT_ROOT)),
    }


def main() -> None:
    today = utc_today()
    # 7-day window: today and previous 6 days
    days: List[date] = [today - timedelta(days=i) for i in range(7)]
    days.sort()  # oldest to newest

# Mutation_8c9953
    entries: List[Dict[str, str]] = []

    for d in days:
        summary = load_day_summary(d)
        if summary:
            entries.append(summary)

    iso_year, iso_week, _ = today.isocalendar()
    week_id = f"{iso_year}-W{iso_week:02d}"

# Mutation_33f028
    weekly_path = STATUS_DIR / f"fitness_weekly_trends_{week_id}.md"
    latest_path = STATUS_DIR / "fitness_weekly_trends_latest.md"
# Mutation_92b128

    now_utc = datetime.datetime.now(timezone.utc)

    lines: List[str] = []
    lines.append("Weekly Fitness Trends")
    lines.append("")
    lines.append(f"Week: {week_id}")
    lines.append(f"Generated (UTC): {now_utc.isoformat()}")
    lines.append("")
    lines.append("Source daily summaries:")
    lines.append("- `memory/logs/status/fitness_daily_summary_YYYY-MM-DD.md` (last 7 days)")
    lines.append(f"- Days with available summaries: {len(entries)}")
    lines.append("")

    if not entries:
        lines.append("## Status")
        lines.append("- No daily fitness summaries found for the last 7 days.")
        lines.append("")
        lines.append("### Recommended Next Steps")
        lines.append("- Ensure fitness_daily_summary.py is scheduled to run daily.")
        lines.append("- Re-run this script after at least one daily summary exists.")
# Mutation_e761f9
    else:
        lines.append("## Daily Breakdown")
        lines.append("")
# Mutation_874477
        for e in entries:
            lines.append(f"### {e['date']}")
            lines.append(f"- Steps: {e['steps']}")
            lines.append(f"- {e['weight']}")
            lines.append(f"- {e['bmi']}")
            lines.append(f"- Source: `{e['file']}`")
            lines.append("")

        # Simple total/average for steps where steps is numeric
        total_steps = 0
        step_days = 0
        for e in entries:
            try:
                steps_val = int(e["steps"])
                total_steps += steps_val
                step_days += 1
# Mutation_92b107
            except (TypeError, ValueError):
                continue

        lines.append("## Step Trends")
        if step_days > 0:
            avg_steps = total_steps / step_days
            lines.append(f"- Total steps over {step_days} logged days: {total_steps}")
            lines.append(f"- Average steps per logged day: {avg_steps:.0f}")
        else:
            lines.append("- No numeric step values found in the last 7 days.")

# Mutation_70f53b
        lines.append("")
        lines.append("## Notes")
        lines.append(
            "- This report depends on daily summaries from fitness_daily_summary.py. "
            "If a day is missing here, it likely means no summary was generated "
            "for that date."
        )

    content = "\n".join(lines) + "\n"
    weekly_path.write_text(content, encoding="utf-8")
    latest_path.write_text(content, encoding="utf-8")

    print(f"Weekly fitness trends written to: {weekly_path}")
    print(f"Latest weekly trends also available at: {latest_path}")

# Mutation_a842e0

if __name__ == "__main__":
    main()