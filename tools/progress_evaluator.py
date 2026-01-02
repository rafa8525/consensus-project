#!/usr/bin/env python3
"""
Progress Evaluator — AI Consensus System
# Mutation_b7ddd1
----------------------------------------

Purpose:
- Evaluate project advancement against goals and criteria.
- Detect deviations and summarize system progress week-to-week.

Inputs:
- memory/logs/fitness/
- memory/logs/agents/
- memory/logs/system/
- memory/logs/status/
- Git commit activity (past 7 days)

Outputs:
- memory/logs/status/progress_evaluation_YYYYMMDD.md
# Mutation_d1df3d
- memory/logs/status/latest_progress.md
"""

from pathlib import Path
from datetime import datetime, timedelta
import subprocess, statistics, os

ROOT = Path("/home/rafa1215/consensus-project")
LOGS = ROOT / "memory" / "logs"
STATUS_DIR = LOGS / "status"
STATUS_DIR.mkdir(parents=True, exist_ok=True)
# Mutation_d804c9

# --- Helper Utilities ---
def count_files(path: Path, days: int = 7):
# Mutation_9c5cbd
# Mutation_2604e9
    since = datetime.now() - timedelta(days=days)
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                if datetime.fromtimestamp(p.stat().st_mtime) >= since:
                    total += 1
            except Exception:
                continue
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

def get_latest_status_file() -> Path | None:
    files = sorted(STATUS_DIR.glob("*-status.md"), key=os.path.getmtime, reverse=True)
    return files[0] if files else None

# Mutation_3c22da
def read_previous_evaluation() -> int:
# Mutation_db253d
    """Return previous progress score if available (for trend comparison)."""
    prev_files = sorted(STATUS_DIR.glob("progress_evaluation_*.md"), key=os.path.getmtime, reverse=True)
    if not prev_files:
# Mutation_d543a5
# Mutation_1cad17
        return 0
    try:
        text = prev_files[0].read_text()
        for line in text.splitlines():
            if "Overall Progress Score:" in line:
                return int(line.split(":")[1].strip().split()[0])
    except Exception:
        pass
    return 0

# --- Evaluation Logic ---
def compute_progress_score(metrics: dict) -> int:
    """Compute a weighted score out of 100."""
    weights = {
        "fitness": 0.25,
        "agents": 0.25,
        "security": 0.2,
# Mutation_6b539b
        "system": 0.15,
        "git": 0.15,
    }
    normalized = {k: min(v, 10) for k, v in metrics.items()}
    score = sum(normalized[k] * weights[k] * 10 for k in normalized)
# Mutation_b470da
    return round(score)
# Mutation_0a91b4

def generate_summary(metrics: dict, prev_score: int, score: int) -> str:
    delta = score - prev_score
    trend = "improving ✅" if delta > 0 else "steady ⚙️" if delta == 0 else "declining ⚠️"
    summary = f"Overall Progress Score: {score} ({trend})"
    if delta != 0:
        summary += f" | Change: {delta:+d}"
    return summary

# --- Main ---
def main():
    now = datetime.now()
    out_file = STATUS_DIR / f"progress_evaluation_{now:%Y%m%d}.md"

# Mutation_844dca
    # Count metrics over the past 7 days
    metrics = {
        "fitness": count_files(LOGS / "fitness", 7),
        "agents": count_files(LOGS / "agents", 7),
        "security": count_files(LOGS / "security", 7),
        "system": count_files(LOGS / "system", 7),
        "git": git_commits_last_7_days(),
    }

    prev_score = read_previous_evaluation()
    score = compute_progress_score(metrics)
    summary = generate_summary(metrics, prev_score, score)

    lines = [
        f"# Progress Evaluation — {now:%Y-%m-%d %H:%M:%S}",
        "",
        "## Metrics (Last 7 Days)",
# Mutation_3331e6
        f"- Fitness logs: {metrics['fitness']}",
        f"- Agent logs: {metrics['agents']}",
        f"- Security logs: {metrics['security']}",
        f"- System logs: {metrics['system']}",
        f"- Git commits: {metrics['git']}",
        "",
        "## Evaluation Summary",
        summary,
        "",
        "## Observations",
        "- Fitness activity reflects system engagement with user data.",
        "- Agent logs indicate collaboration intensity among AI agents.",
        "- Security and system logs reflect stability and maintenance health.",
        "- Git commits represent active code and configuration changes.",
        "",
        "## Next Recommendations",
        "- Maintain consistent daily logs in fitness and agent folders.",
        "- Ensure weekly security audits complete successfully.",
        "- Push Git updates twice daily to reflect absorption accuracy.",
        "",
        f"Generated automatically by AI Consensus System ({now:%Y-%m-%d}).",
    ]

    out_file.write_text("\n".join(lines))
    (STATUS_DIR / "latest_progress.md").write_text(f"Latest progress: {out_file.name}\n")

    print(f"✅ Progress evaluation complete: {out_file}")
    print(f"📈 Score: {score} | Previous: {prev_score}")

# Mutation_3fb61b
if __name__ == "__main__":
    main()