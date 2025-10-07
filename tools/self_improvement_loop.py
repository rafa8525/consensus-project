#!/usr/bin/env python3
"""
Recursive Self-Improvement Loop — AI Consensus System
-----------------------------------------------------

Purpose:
Continuously improve system performance by:
1. Reading outputs from all core modules (status, audits, VPN, fitness, etc.)
2. Detecting recurring issues, anomalies, or stagnation.
3. Generating actionable recommendations.
4. Logging weekly AI-driven insights for human review.

Outputs:
- memory/logs/system/self_improvement_YYYYWW.md
- memory/logs/system/latest_self_improvement.md
"""

from pathlib import Path
from datetime import datetime, timedelta
import os, statistics, re

ROOT = Path("/home/rafa1215/consensus-project")
LOG_DIR = ROOT / "memory" / "logs" / "system"
STATUS_DIR = ROOT / "memory" / "logs" / "status"
FITNESS_DIR = ROOT / "memory" / "logs" / "fitness"
LOG_DIR.mkdir(parents=True, exist_ok=True)

TARGET_SCORE = 85   # ideal progress benchmark
TREND_WINDOW = 4    # weeks

# --- Utilities ------------------------------------------------------------

def read_last_lines(path: Path, n=50):
    """Read last N lines of a text file safely."""
    if not path.exists():
        return []
    try:
        lines = path.read_text().splitlines()
        return lines[-n:]
    except Exception:
        return []

def extract_score(lines):
    """Find numeric progress score from evaluation file."""
    for line in lines:
        m = re.search(r"Overall Progress Score:\s*(\d+)", line)
        if m:
            return int(m.group(1))
    return None

def list_recent_files(folder: Path, pattern: str, days: int = 30):
    since = datetime.now() - timedelta(days=days)
    return [p for p in folder.glob(pattern) if p.is_file() and p.stat().st_mtime >= since.timestamp()]

# --- Analysis -------------------------------------------------------------

def analyze_progress_trend():
    """Compute trend of weekly progress scores."""
    files = sorted(STATUS_DIR.glob("progress_evaluation_*.md"), key=os.path.getmtime, reverse=True)[:TREND_WINDOW]
    scores = []
    for f in files:
        score = extract_score(read_last_lines(f))
        if score is not None:
            scores.append(score)
    if not scores:
        return (0, "⚠️ No progress data found.")
    avg = statistics.mean(scores)
    trend = "improving" if len(scores) > 1 and scores[0] > scores[-1] else "steady" if len(set(scores)) == 1 else "declining"
    return (avg, f"Trend: {trend} (avg={avg:.1f})")

def detect_common_failures():
    """Scan recent system logs for warnings or failures."""
    fails = []
    for p in list_recent_files(LOG_DIR, "*.md", 14):
        text = p.read_text()
        for marker in ["❌", "⚠️", "Timeout", "failed", "error"]:
            if marker.lower() in text.lower():
                fails.append(p.name)
                break
    return fails

def recommend_actions(avg_score, fails):
    recs = []
    if avg_score < TARGET_SCORE:
        recs.append("Increase fitness data frequency or agent collaboration intensity.")
    if fails:
        recs.append(f"Investigate recurring issues in {len(fails)} recent logs.")
    if avg_score >= TARGET_SCORE and not fails:
        recs.append("System operating optimally — no action required.")
    recs.append("Re-run full bootstrap if metrics stagnate for >2 weeks.")
    return recs

# --- Main ----------------------------------------------------------------

def main():
    now = datetime.now()
    y, w, _ = now.isocalendar()
    out_file = LOG_DIR / f"self_improvement_{y}W{w:02d}.md"

    avg_score, trend_msg = analyze_progress_trend()
    fails = detect_common_failures()
    recs = recommend_actions(avg_score, fails)

    lines = [
        f"# Self-Improvement Report — Week {y}-W{w:02d}",
        f"Generated: {now:%Y-%m-%d %H:%M:%S}",
        "",
        f"## Progress Overview",
        f"- {trend_msg}",
        f"- Average Score (last {TREND_WINDOW} weeks): {avg_score:.1f}",
        "",
        "## Detected Issues",
        f"- Failures or warnings: {len(fails)}",
    ]
    if fails:
        lines += [f"  - {f}" for f in fails]
    lines += [
        "",
        "## Recommended Actions",
    ] + [f"- {r}" for r in recs] + [
        "",
        "## Notes",
        "This module analyzes recent metrics and provides guidance; it never changes code directly.",
        "Adjust recommendations manually or review via system_bootstrap after implementing fixes.",
    ]

    out_file.write_text("\n".join(lines))
    (LOG_DIR / "latest_self_improvement.md").write_text(f"Latest report: {out_file.name}\n")

    print(f"✅ Self-improvement loop executed → {out_file}")
    print(f"📈 Average score: {avg_score:.1f}")
    print(f"📎 Pointer updated → latest_self_improvement.md")

if __name__ == "__main__":
    main()
