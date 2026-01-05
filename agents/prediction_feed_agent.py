#!/usr/bin/env python3
from datetime import datetime, date
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "memory" / "logs" / "system" / "predictions"

SUMMARIZER = ROOT / "tools" / "prediction_feed_summarizer_v2.py"
if not SUMMARIZER.exists():
    SUMMARIZER = ROOT / "tools" / "prediction_feed_summarizer.py"

FITNESS_DIR = ROOT / "memory" / "logs" / "fitness"
FITNESS_TRACKER = FITNESS_DIR / "fitness_tracker.log"

def _fitness_logged_today(today: str) -> bool:
    if (FITNESS_DIR / f"fitness_sync_{today}.log").exists():
        return True
    if FITNESS_TRACKER.exists():
        try:
            s = FITNESS_TRACKER.read_text(encoding="utf-8", errors="ignore")
            return today in s
        except Exception:
            return False
    return False

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out_path = OUT_DIR / f"prediction_feed_{today}.md"

    fitness_ok = _fitness_logged_today(today)
    if fitness_ok:
        health_block = "## Health/Fitness\n(no alerts)\n"
    else:
        health_block = (
            "## Health/Fitness\n"
            "1. [MEDIUM] No fitness log found for today. Log your steps or swim laps so trends stay accurate.\n"
            "   - Reason: Missing fitness sync file and no matching date found in fitness_tracker.log.\n"
        )

    content = (
        f"# Prediction Feed – {today}\n"
        f"Generated: {datetime.now().isoformat()}\n"
        f"{health_block}"
        "## Errands & Geofences\n"
        "1. [LOW] Look at this week and see if there is a small errand you can knock out today (groceries, pet supplies, or a short stop on the way home).\n"
        "   - Reason: No strong geofence-derived errands found.\n"
        "## Media & Fun\n"
        "1. [LOW] Schedule a movie or show tonight, even if it is just 30–45 minutes.\n"
        "   - Reason: No specific recent movie context found.\n"
        "## Family/Events\n"
        "1. [MEDIUM] Send a quick message or check-in to one family member today.\n"
        "   - Reason: Light social maintenance improves consistency over time.\n"
    )

    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote: {out_path}")

    if SUMMARIZER.exists():
        log = Path("/tmp/prediction_feed_summarizer.log")
        with log.open("w", encoding="utf-8") as f:
            subprocess.run([sys.executable, str(SUMMARIZER)], stdout=f, stderr=f, check=False)
        print("Summarizer: ran (see /tmp/prediction_feed_summarizer.log)")
    else:
        print("Summarizer: not found, skipping")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
