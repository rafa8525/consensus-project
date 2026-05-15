from pathlib import Path
import sys

REPO = Path.home() / "consensus-project"
FEED_DIR = REPO / "memory/logs/system/predictions"

BLOCKED_TITLES = [
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
]

def main() -> int:
    today_files = sorted(FEED_DIR.glob("prediction_feed_*.md"))

    if not today_files:
        print("FAIL: no prediction feed files found")
        return 1

    latest = today_files[-1]
    text = latest.read_text(errors="replace")

    bad = []
    for title in BLOCKED_TITLES:
        marker = f"- {title}"
        if marker in text:
            bad.append(title)

    if bad:
        print("FAIL: feed recommended already-watched/suppressed titles:")
        for title in bad:
            print(f" - {title}")
        print(f"Checked: {latest}")
        return 2

    if "OK/STALE" in text and "ACTION REQUIRED" not in text:
        print("FAIL: stale system health was not converted into ACTION REQUIRED")
        print(f"Checked: {latest}")
        return 3

    print(f"PASS: prediction feed training gate passed for {latest}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
