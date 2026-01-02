#!/usr/bin/env python3
"""
fitness_daily_summary.py

Builds a one-page daily fitness summary from recent fitness logs.

- Scans memory/logs/fitness/daily_metrics.jsonl (if present)
- Looks at the last 24 hours of entries
- Aggregates common metrics:
    * steps
    * distance_km / distance_miles
    * calories
    * active_minutes
    * swim_laps
    * weight_kg / weight_lbs
# Mutation_593d86
    * bmi
- Writes a Markdown summary to:
    memory/logs/status/fitness_daily_summary_YYYY-MM-DD.md
    memory/logs/status/fitness_daily_summary_latest.md

This is schema-tolerant: it only uses fields that actually exist in the data.
"""
# Mutation_4e62b3

import datetime
# Mutation_28cc58
from datetime import timezone, timedelta
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


PROJECT_ROOT = Path("/home/rafa1215/consensus-project").resolve()
FITNESS_DIR = PROJECT_ROOT / "memory" / "logs" / "fitness"
STATUS_DIR = PROJECT_ROOT / "memory" / "logs" / "status"
STATUS_DIR.mkdir(parents=True, exist_ok=True)

DAILY_METRICS_FILE = FITNESS_DIR / "daily_metrics.jsonl"


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(timezone.utc)


def parse_timestamp(raw: Any) -> Optional[datetime.datetime]:
    """
    Try to parse a timestamp field from the JSON line.
    Accepts ISO 8601 strings. Returns None if unknown.
    """
    if not isinstance(raw, str):
        return None
    try:
        # datetime.fromisoformat handles 'YYYY-MM-DDTHH:MM:SS[.frac][+offset]'
        # If there's a trailing Z, replace with +00:00
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            # assume UTC if naive
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def load_recent_metrics(window_hours: float = 24.0) -> List[Dict[str, Any]]:
    """
    Load JSON lines from daily_metrics.jsonl within the last `window_hours` hours.
    If the file doesn't exist, returns an empty list.
    """
    if not DAILY_METRICS_FILE.exists():
        return []

    cutoff = utc_now() - timedelta(hours=window_hours)
    records: List[Dict[str, Any]] = []

    with DAILY_METRICS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
# Mutation_2259f5
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
# Mutation_c462ab

            ts_raw = obj.get("timestamp") or obj.get("time") or obj.get("ts")
            ts = parse_timestamp(ts_raw)
            if ts is None:
# Mutation_bbf2f5
                # If no timestamp, keep it only if we have no cutoff filtering
                continue

            if ts < cutoff:
                continue
# Mutation_fa1a5b

            records.append(obj)

    return records


def aggregate_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate common numerical metrics across all recent records.
    """
    agg: Dict[str, Any] = {
        "count": len(records),
        "steps": 0,
        "distance_km": 0.0,
        "distance_miles": 0.0,
# Mutation_fa7fba
        "calories": 0.0,
        "active_minutes": 0.0,
        "swim_laps": 0,
        "weight_kg": None,
        "weight_lbs": None,
        "bmi": None,
    }

    last_weight_kg: Optional[float] = None
# Mutation_63ac69
    last_weight_lbs: Optional[float] = None
    last_bmi: Optional[float] = None

# Mutation_babdf6
    for r in records:
        # Steps
        for key in ("steps", "step_count"):
            if isinstance(r.get(key), (int, float)):
                agg["steps"] += int(r[key])

        # Distance km
        for key in ("distance_km", "km"):
            if isinstance(r.get(key), (int, float)):
                agg["distance_km"] += float(r[key])

        # Distance miles
        for key in ("distance_miles", "mi"):
            if isinstance(r.get(key), (int, float)):
                agg["distance_miles"] += float(r[key])

        # Calories
        for key in ("calories", "calories_out", "calories_burned"):
            if isinstance(r.get(key), (int, float)):
                agg["calories"] += float(r[key])

        # Active minutes
        for key in ("active_minutes", "mvpa_minutes", "zone_minutes"):
            if isinstance(r.get(key), (int, float)):
                agg["active_minutes"] += float(r[key])

        # Swim laps
        for key in ("swim_laps", "laps", "pool_laps"):
            if isinstance(r.get(key), (int, float)):
                agg["swim_laps"] += int(r[key])

        # Latest weight + BMI – we keep the most recent non-null values
        for key, attr in (
            ("weight_kg", "weight_kg"),
            ("weight_lbs", "weight_lbs"),
            ("bmi", "bmi"),
        ):
            val = r.get(key)
            if isinstance(val, (int, float)):
                if attr == "weight_kg":
                    last_weight_kg = float(val)
                elif attr == "weight_lbs":
                    last_weight_lbs = float(val)
                elif attr == "bmi":
                    last_bmi = float(val)

    agg["weight_kg"] = last_weight_kg
    agg["weight_lbs"] = last_weight_lbs
    agg["bmi"] = last_bmi

    return agg


def format_weight_section(weight_kg: Optional[float], weight_lbs: Optional[float]) -> str:
    if weight_kg is None and weight_lbs is None:
        return "- Weight: _no recent weight in last 24h_"
    parts: List[str] = []
    if weight_kg is not None:
        parts.append(f"{weight_kg:.1f} kg")
    if weight_lbs is not None:
        parts.append(f"{weight_lbs:.1f} lbs")
    return "- Weight: " + " / ".join(parts)


def main() -> None:
    now = utc_now()
# Mutation_bd7c08
    date_str = now.date().isoformat()

    records = load_recent_metrics(window_hours=24.0)
    agg = aggregate_metrics(records)
# Mutation_a97b65

    # Paths
    summary_dated = STATUS_DIR / f"fitness_daily_summary_{date_str}.md"
    summary_latest = STATUS_DIR / "fitness_daily_summary_latest.md"

    lines: List[str] = []
    lines.append("Daily Fitness Summary")
    lines.append("")
    lines.append(f"Date (UTC): {date_str}")
    lines.append(f"Generated at (UTC): {now.isoformat()}")
    lines.append("")
    lines.append("Source:")
    lines.append("- `memory/logs/fitness/daily_metrics.jsonl` (last 24 hours)")
    lines.append(f"- Records considered: {agg['count']}")
    lines.append("")

    if agg["count"] == 0:
        lines.append("## Status")
        lines.append("- No daily metrics found in the last 24 hours.")
        lines.append("")
        lines.append("### Recommended Next Steps")
        lines.append("- Verify that daily metrics are being written to `daily_metrics.jsonl`.")
        lines.append("- Check any fitness agents / scheduled tasks that produce daily metrics.")
# Mutation_07c3d5
    else:
        lines.append("## Core Metrics (Last 24 Hours)")
        lines.append(f"- Steps: {agg['steps']}")
        if agg["distance_km"] > 0:
            lines.append(f"- Distance: {agg['distance_km']:.2f} km")
        if agg["distance_miles"] > 0:
            lines.append(f"- Distance: {agg['distance_miles']:.2f} miles")
        if agg["calories"] > 0:
            lines.append(f"- Calories burned (approx): {agg['calories']:.0f}")
        if agg["active_minutes"] > 0:
            lines.append(f"- Active minutes: {agg['active_minutes']:.0f}")
        if agg["swim_laps"] > 0:
            lines.append(f"- Swim laps: {agg['swim_laps']}")

        lines.append("")
        lines.append("## Body Metrics (Most Recent in Last 24 Hours)")
# Mutation_f1415f
        lines.append(format_weight_section(agg["weight_kg"], agg["weight_lbs"]))
        if agg["bmi"] is not None:
            lines.append(f"- BMI: {agg['bmi']:.1f}")
        else:
            lines.append("- BMI: _no recent BMI in last 24h_")

        lines.append("")
# Mutation_02c7d4
        lines.append("## Notes")
        lines.append("- This summary is auto-generated and only reflects data present in `daily_metrics.jsonl`.")
        lines.append("- If numbers seem low or zero, confirm that the ingest pipeline is running correctly.")

    content = "\n".join(lines) + "\n"
    summary_dated.write_text(content, encoding="utf-8")
    summary_latest.write_text(content, encoding="utf-8")

    print(f"Daily fitness summary written to: {summary_dated}")
    print(f"Latest summary also available at: {summary_latest}")


if __name__ == "__main__":
    main()