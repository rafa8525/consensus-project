#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEED_DIR = ROOT / "memory" / "logs" / "system" / "predictions"
OUT_DIR  = ROOT / "memory" / "logs" / "status"

SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
SECTION_OK_RE = re.compile(r"^\(no alerts\)\s*$")
ITEM_RE    = re.compile(r"^\s*\d+\.\s+\[(LOW|MEDIUM|HIGH)\]\s+(.+?)\s*$")
REASON_RE  = re.compile(r"^\s*-\s*Reason:\s*(.+?)\s*$")

@dataclass
class Pred:
    section: str
    priority: str
    text: str
    reason: str | None = None

def newest_feed() -> Path | None:
    if not FEED_DIR.exists():
        return None
    feeds = sorted(FEED_DIR.glob("prediction_feed_*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
    return feeds[0] if feeds else None

def parse(feed_text: str) -> tuple[list[Pred], list[str], list[str]]:
    preds: list[Pred] = []
    sections_seen: list[str] = []
    ok_sections: list[str] = []
    section = "Uncategorized"
    pending: Pred | None = None
    saw_item_in_section = False
    saw_ok_in_section = False

    def _close_section(sec: str) -> None:
        # Skip placeholder unless it actually had content signals
        if sec == "Uncategorized" and (not saw_item_in_section) and (not saw_ok_in_section):
            return
        if sec not in sections_seen:
            sections_seen.append(sec)
        if (not saw_item_in_section) and saw_ok_in_section:
            if sec not in ok_sections:
                ok_sections.append(sec)

    for raw in feed_text.splitlines():
        line = raw.rstrip("\n")

        m = SECTION_RE.match(line)
        if m:
            # close previous section before switching
            _close_section(section)
            section = m.group(1).strip()
            pending = None
            saw_item_in_section = False
            saw_ok_in_section = False
            continue

        if SECTION_OK_RE.match(line.strip()):
            saw_ok_in_section = True
            continue

        m = ITEM_RE.match(line)
        if m:
            saw_item_in_section = True
            pending = Pred(section=section, priority=m.group(1), text=m.group(2).strip())
            preds.append(pending)
            continue

        m = REASON_RE.search(line)
        if m and pending is not None and pending.reason is None:
            pending.reason = m.group(1).strip()

    # close final section
    _close_section(section)

    # Remove placeholder Uncategorized if it never appeared as a real header
    # (but keep it if it actually had content)
    return preds, sections_seen, ok_sections

def main() -> int:
    feed = newest_feed()
    if feed is None:
        print("No prediction_feed_*.md found.")
        return 1

    text = feed.read_text(encoding="utf-8", errors="replace")
    preds, sections_seen, ok_sections = parse(text)

    # Extract date from filename: prediction_feed_YYYY-MM-DD.md
    d = feed.stem.replace("prediction_feed_", "")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"prediction_feed_summary_{d}.md"
    latest_path = OUT_DIR / "prediction_feed_summary_latest.md"

    now_utc = datetime.now(timezone.utc).isoformat()

    highs = [p for p in preds if p.priority == "HIGH"]
    meds  = [p for p in preds if p.priority == "MEDIUM"]
    lows  = [p for p in preds if p.priority == "LOW"]

    lines: list[str] = []
    lines.append("Prediction Feed Summary")
    lines.append(f"Source file: `{feed.as_posix().replace(str(ROOT) + '/', '')}`")
    lines.append(f"Generated at (UTC): {now_utc}")
    lines.append(f"Predictions parsed: {len(preds)}")
    lines.append(f"Sections seen: {len(sections_seen)}")
    if ok_sections:
        lines.append(f"Sections with no actionable items: {', '.join(ok_sections)}")
    else:
        lines.append("Sections with no actionable items: (none)")
    lines.append("")

    lines.append("## Alerts & Risk Snapshot")
    if highs:
        lines.append(f"- HIGH alerts: {len(highs)}")
    else:
        lines.append("- HIGH alerts: 0")
    lines.append(f"- MEDIUM items: {len(meds)}")
    lines.append(f"- LOW items: {len(lows)}")
    lines.append("")

    lines.append("## Predictions")
    if not preds:
        lines.append("(none parsed)")
    else:
        for i, p0 in enumerate(preds, 1):
            lines.append(f"### {i}. [{p0.priority}] {p0.section}")
            lines.append(f"- Text: {p0.text}")
            if p0.reason:
                lines.append(f"- Reason: {p0.reason}")
            lines.append("")

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    latest_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    print(f"Prediction feed summary written to: {out_path}")
    print(f"Latest summary also available at: {latest_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
