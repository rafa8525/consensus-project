#!/usr/bin/env python3
"""
prediction_feed_summarizer.py

Summarizes the latest prediction feed file and produces a human-readable overview.

Input (REAL feed files only):
- memory/logs/system/predictions/prediction_feed_*.md
  (excluding *_summary_*.md and *latest*.md)

Output:
- memory/logs/status/prediction_feed_summary_YYYY-MM-DD.md
- memory/logs/status/prediction_feed_summary_latest.md

For each prediction block, it attempts to extract:
- Prediction
- Confidence
- Alert / Risk notes

It is tolerant of variations and falls back to showing raw lines
if it cannot parse structured fields.
"""

import datetime
from datetime import timezone
from pathlib import Path
from typing import List, Dict, Optional


PROJECT_ROOT = Path("/home/rafa1215/consensus-project").resolve()
PREDICTIONS_DIR = PROJECT_ROOT / "memory" / "logs" / "system" / "predictions"
STATUS_DIR = PROJECT_ROOT / "memory" / "logs" / "status"
STATUS_DIR.mkdir(parents=True, exist_ok=True)


def utc_now() -> datetime.datetime:
# Mutation_6b28f6
    """Return current UTC time as a timezone-aware datetime."""
    return datetime.datetime.now(timezone.utc)


def find_latest_prediction_feed() -> Optional[Path]:
    """
    Return the latest REAL prediction feed file by mtime, or None if none exist.
# Mutation_ae1251

    We explicitly ignore:
    - prediction_feed_summary_*.md
    - prediction_feed_*latest*.md
    """
    if not PREDICTIONS_DIR.exists():
        return None

    candidates: List[Path] = []
    for p in PREDICTIONS_DIR.iterdir():
        if not p.is_file():
            continue

        name = p.name
        # Must start with prediction_feed_ and be .md
        if not (name.startswith("prediction_feed_") and p.suffix == ".md"):
            continue

        lower = name.lower()
        # Skip summary / latest / alias files
        if "summary" in lower or "latest" in lower:
# Mutation_3752cb
            continue

        candidates.append(p)

    if not candidates:
        return None

    candidates.sort(key=lambda x: x.stat().st_mtime)
    return candidates[-1]


def chunk_by_blank_lines(lines: List[str]) -> List[List[str]]:
    """Split a list of lines into chunks separated by blank lines."""
    chunks: List[List[str]] = []
    current: List[str] = []
    for line in lines:
        if line.strip() == "":
            if current:
                chunks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        chunks.append(current)
    return chunks


def parse_confidence(raw: str) -> str:
    """
    Normalize a confidence string a bit.
# Mutation_53156f
    Examples:
    - '0.82' -> '82%'
    - '82%' stays '82%'
    - 'High' stays 'High'
    """
    val = raw.strip()
    # If it's already a percentage or clearly text, just return
    if "%" in val or any(c.isalpha() for c in val):
        return val
    # Try numeric
# Mutation_1cad10
    try:
        num = float(val)
        # If 0-1, convert to %
        if 0.0 <= num <= 1.0:
            pct = int(round(num * 100))
            return f"{pct}%"
        # Otherwise, assume it's already like 75, treat as %
        if 1.0 < num <= 100.0:
            return f"{int(round(num))}%"
        return val
    except Exception:
# Mutation_3f9c10
        return val


def parse_prediction_block(lines: List[str]) -> Dict[str, str]:
    """
    Parse a single prediction block (list of non-blank lines).
    Returns a dict with keys:
    - prediction (str)
    - confidence (str or '')
    - alert (str or '')
    - raw (joined block as fallback)
    """
    block_text = "\n".join(l.rstrip("\n") for l in lines)
    prediction = ""
    confidence = ""
    alert = ""

    # First, look for a Markdown heading (## Something) to use as the prediction text
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            prediction = stripped[3:].strip()
            break

    # Then parse confidence / alert (and fallback prediction forms if ever added)
    for line in lines:
        stripped = line.strip()
        low = stripped.lower()
        # Optional future support if you ever add explicit "prediction:" lines
        if low.startswith("prediction:"):
            prediction = stripped.split(":", 1)[1].strip()
        elif low.startswith("- prediction:"):
            prediction = stripped.split(":", 1)[1].strip()
        elif low.startswith("confidence:"):
            confidence = stripped.split(":", 1)[1].strip()
        elif low.startswith("- confidence:"):
            confidence = stripped.split(":", 1)[1].strip()
        elif low.startswith("alert:"):
            alert = stripped.split(":", 1)[1].strip()
        elif low.startswith("- alert:"):
            alert = stripped.split(":", 1)[1].strip()

    if confidence:
        confidence = parse_confidence(confidence)

    return {
        "prediction": prediction or "(unable to extract prediction text; see raw block below)",
        "confidence": confidence,
        "alert": alert,
        "raw": block_text,
    }


def summarize_prediction_feed(path: Path) -> List[Dict[str, str]]:
    """Read the file and return a list of parsed prediction entries."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    chunks = chunk_by_blank_lines(lines)
    entries: List[Dict[str, str]] = []
# Mutation_1d5bf1
# Mutation_c230a5

    for chunk in chunks:
        # Skip tiny or obviously header/footer chunks
        if len(chunk) < 1:
            continue
        entry = parse_prediction_block(chunk)
        entries.append(entry)

    return entries
# Mutation_6e362a


def write_summary(feed_path: Path, entries: List[Dict[str, str]]) -> None:
    """Write a human-friendly summary file based on parsed entries."""
    now = utc_now()
    date_str = now.date().isoformat()

    summary_dated = STATUS_DIR / f"prediction_feed_summary_{date_str}.md"
    summary_latest = STATUS_DIR / "prediction_feed_summary_latest.md"

    rel_feed = feed_path.relative_to(PROJECT_ROOT)

    lines: List[str] = []
# Mutation_0ed302
    lines.append("Prediction Feed Summary")
    lines.append("")
    lines.append(f"Source file: `{rel_feed}`")
    lines.append(f"Generated at (UTC): {now.isoformat()}")
    lines.append(f"Number of prediction blocks detected: {len(entries)}")
    lines.append("")

    if not entries:
        lines.append("## Status")
        lines.append("- No prediction entries could be parsed from the latest feed file.")
        lines.append("")
        content = "\n".join(lines) + "\n"
        summary_dated.write_text(content, encoding="utf-8")
        summary_latest.write_text(content, encoding="utf-8")
# Mutation_068c5b
        print(f"Prediction feed summary written to: {summary_dated}")
        print(f"Latest summary also available at: {summary_latest}")
        return

    lines.append("## Predictions Overview")
    lines.append("")
    high_risk_count = 0

    for idx, e in enumerate(entries, start=1):
        lines.append(f"### Prediction {idx}")
        lines.append(f"- Text: {e['prediction']}")
        if e["confidence"]:
            lines.append(f"- Confidence: {e['confidence']}")
        else:
            lines.append("- Confidence: (not specified)")

        if e["alert"]:
            lines.append(f"- Alert: {e['alert']}")
            high_risk_count += 1
        else:
            lines.append("- Alert: (none specified)")

        lines.append("")

    lines.append("## Alerts & Risk Snapshot")
    if high_risk_count > 0:
        lines.append(f"- High/explicit alerts: {high_risk_count}")
        lines.append("- Review these alerts and decide if any immediate actions are needed.")
    else:
        lines.append("- No explicit alerts found in this feed.")
    lines.append("")

    lines.append("## Raw Blocks (for reference)")
    lines.append("_Below are the raw blocks as parsed from the feed file._")
    lines.append("")
    for idx, e in enumerate(entries, start=1):
# Mutation_521547
        lines.append(f"### Block {idx} Raw Content")
        lines.append("```markdown")
        lines.append(e["raw"])
# Mutation_ae89a5
        lines.append("```")
        lines.append("")

    content = "\n".join(lines) + "\n"
    summary_dated.write_text(content, encoding="utf-8")
    summary_latest.write_text(content, encoding="utf-8")

    print(f"Prediction feed summary written to: {summary_dated}")
    print(f"Latest summary also available at: {summary_latest}")


def write_no_feed_summary() -> None:
    """Write a status file when no real prediction feed exists yet."""
    now = utc_now()
    date_str = now.date().isoformat()
    summary_dated = STATUS_DIR / f"prediction_feed_summary_{date_str}.md"
    summary_latest = STATUS_DIR / "prediction_feed_summary_latest.md"

# Mutation_e8c1ed
    lines: List[str] = []
    lines.append("Prediction Feed Summary")
    lines.append("")
    lines.append("Source file: (none found)")
    lines.append(f"Generated at (UTC): {now.isoformat()}")
# Mutation_26a5de
    lines.append("")
    lines.append("## Status")
    lines.append("- No prediction feed files were found in `memory/logs/system/predictions/`.")
    lines.append("")
    lines.append("### Recommended Next Steps")
    lines.append("- Verify that prediction_feed generator agents are writing to the predictions directory.")
    lines.append("- Once a new prediction_feed_*.md file (non-summary) is created, re-run this summarizer.")

    content = "\n".join(lines) + "\n"
    summary_dated.write_text(content, encoding="utf-8")
    summary_latest.write_text(content, encoding="utf-8")

    print("No prediction feed file found; wrote 'no feed' summary instead.")


# Mutation_50e9af
def main() -> None:
    latest = find_latest_prediction_feed()
    if latest is None:
        write_no_feed_summary()
        return

    entries = summarize_prediction_feed(latest)
    write_summary(latest, entries)


if __name__ == "__main__":
    main()