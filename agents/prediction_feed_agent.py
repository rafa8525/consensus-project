#!/usr/bin/env python3
from datetime import datetime, date
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "memory" / "logs" / "system" / "predictions"
SUMMARIZER = ROOT / "tools" / "prediction_feed_summarizer.py"

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out_path = OUT_DIR / f"prediction_feed_{today}.md"

    content = f"""# Prediction Feed – {today}
Generated: {datetime.now().isoformat()}
## Health/Fitness
1. [MEDIUM] No fitness log found for today. Log your steps or swim laps so trends stay accurate.
   - Reason: Missing fitness log artifact for today.
## Errands & Geofences
1. [LOW] Look at this week and see if there is a small errand you can knock out today (groceries, pet supplies, or a short stop on the way home).
   - Reason: No strong geofence-derived errands found.
## Media & Fun
1. [LOW] Schedule a movie or show tonight, even if it is just 30–45 minutes.
   - Reason: No specific recent movie context found.
## Family/Events
1. [MEDIUM] Send a quick message or check-in to one family member today.
   - Reason: Light social maintenance improves consistency over time.
"""

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
