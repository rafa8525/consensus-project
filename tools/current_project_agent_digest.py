#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Tuple

VERSION = "v2026-03-17-agent-summaries-modern-2"

KEYWORD_PATTERNS = {
    "fitness": re.compile(r"\b(fitness|fitbit|steps?|swim|laps?|bmi|heart rate|sleep|health)\b", re.I),
    "movies": re.compile(r"\b(movie|movies|streaming|netflix|hulu|max|disney|paramount|apple tv|dark fantasy|superhero)\b", re.I),
    "security": re.compile(r"\b(vpn|security|audit|wi-?fi|encryption|risk)\b", re.I),
    "automation": re.compile(r"\b(task|automation|agent|scheduler|schedule|monitor|status|prediction|health snapshot|orchestrator|heartbeat)\b", re.I),
    "finance": re.compile(r"\b(finance|bill|budget|xfinity|deal|price|grocery|shopping)\b", re.I),
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def collect_docs(root: Path) -> List[Tuple[Path, str]]:
    files: List[Tuple[Path, str]] = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".txt", ".md", ".log", ".json"}:
            files.append((p, read_text(p)))
    return files


def latest_prediction_text(files: List[Tuple[Path, str]]) -> str:
    preds: List[Tuple[Path, str]] = []
    for p, t in files:
        name = p.name.lower()
        if p.suffix.lower() == ".md" and re.match(r"prediction_feed_\d{4}-\d{2}-\d{2}\.md$", name):
            preds.append((p, t))
    if not preds:
        return ""
    preds.sort(key=lambda x: x[0].name)
    return preds[-1][1]


def latest_snapshot_text(files: List[Tuple[Path, str]]) -> str:
    snaps = [(p, t) for p, t in files if p.name.lower() == "system_health_snapshot.md"]
    if not snaps:
        return ""
    snaps.sort(key=lambda x: x[0].as_posix())
    return snaps[-1][1]


def parse_prediction_items(pred_text: str) -> List[dict]:
    items: List[dict] = []
    cur_section = None
    for line in pred_text.splitlines():
        if line.startswith("## "):
            cur_section = line[3:].strip()
            continue
        m = re.match(r"\d+\.\s+\[(?P<sev>[^\]]+)\]\s+(?P<msg>.+)", line.strip())
        if m:
            items.append(
                {
                    "section": cur_section or "General",
                    "severity": m.group("sev").strip(),
                    "message": m.group("msg").strip(),
                }
            )
    return items


def parse_snapshot(snapshot_text: str) -> List[dict]:
    rows: List[dict] = []
    for line in snapshot_text.splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
        if m and m.group(1).strip().lower() != "subsystem":
            rows.append(
                {
                    "subsystem": m.group(1).strip(),
                    "status": m.group(2).strip(),
                    "notes": m.group(3).strip(),
                }
            )
    return rows


def score_doc(name: str, text: str) -> int:
    score = 0
    sample = f"{name}\n{text[:4000]}"
    for pat in KEYWORD_PATTERNS.values():
        score += len(pat.findall(sample))
    return score


def top_relevant_docs(files: List[Tuple[Path, str]], n: int = 8) -> List[Path]:
    ranked = sorted(files, key=lambda ft: score_doc(ft[0].name, ft[1]), reverse=True)
    seen: List[Path] = []
    for p, _ in ranked:
        if p not in seen:
            seen.append(p)
        if len(seen) >= n:
            break
    return seen


def dedupe(items: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        key = re.sub(r"\W+", "", item.lower())
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out


def build_suggestions(pred_items: List[dict], files: List[Tuple[Path, str]]) -> List[str]:
    suggestions: List[str] = []

    if any("No fitness log detected" in i["message"] for i in pred_items):
        suggestions.append("Log today’s fitness activity so weekly summaries and health trends stay accurate.")

    if any("Movie list updated" in i["message"] for i in pred_items):
        suggestions.append("Log your most recent movie watch so the recommendation engine keeps your taste profile fresh.")

    if any("Reunion" in i["message"] for i in pred_items):
        suggestions.append("Do one 5-minute reunion task today: invite, page update, music shortlist, or menu check.")

    for p, t in files:
        n = p.name.lower()
        if "next_steps" in n and "vpn" in t.lower():
            suggestions.append("Finish VPN auto-connect based on Wi-Fi detection; it is still called out as an open next step.")
            break

    if any("System logs updated today" in i["message"] for i in pred_items):
        suggestions.append("Skim the newest system log entry and confirm it is writing to the canonical path you expect.")

    if any("Pick one small errand" in i["message"] for i in pred_items):
        suggestions.append("Knock out one small errand this week so geofence-driven reminders stay relevant to real life.")

    suggestions.append("Review the latest health snapshot after each monitor run so stale subsystems are caught the same day.")
    return dedupe(suggestions)[:10]


def build_optimizations(snapshot_rows: List[dict], files: List[Tuple[Path, str]]) -> List[str]:
    opts: List[str] = []

    for row in snapshot_rows:
        if row["status"].lower() == "warn":
            opts.append(f"Repair or reschedule {row['subsystem']}: {row['notes']}.")

    names = [p.name.lower() for p, _ in files]

    if any("fitness_tracking_system_plan" in n for n in names):
        opts.append("Unify fitness tracking outputs into one daily canonical log so prediction feeds do not depend on scattered inputs.")

    if any("centralized_knowledge_base" in n for n in names):
        opts.append("Publish the new agent summary outputs into the centralized knowledge base so the old showcase layer becomes searchable again.")

    opts.append("Keep health/status files in /home/rafa1215/memory as canonical, then mirror only the human-facing outputs into the repo tree.")
    return dedupe(opts)[:10]


def build_brainstorm(files: List[Tuple[Path, str]], pred_items: List[dict], snapshot_rows: List[dict]) -> List[str]:
    ideas = [
        "Create a single daily executive digest that merges prediction feed, health snapshot, and project next steps into one page.",
        "Add a freshness scoreboard that ranks stale subsystems by impact so the next repair target is obvious.",
        "Attach a 'what changed since yesterday' section to each agent digest to make system drift visible immediately.",
        "Generate one 'wow factor' recommendation daily from your movie, health, or project logs rather than only warnings.",
        "Create an agent-summaries index file so old brainstorms, optimizations, and suggestions remain easy to browse.",
    ]

    if any(row["status"].lower() == "warn" for row in snapshot_rows):
        ideas.append("Trigger an elevated digest whenever overall system health is warn so stale pipelines get surfaced automatically.")

    if any("Movie list updated" in i["message"] for i in pred_items):
        ideas.append("Include a nightly three-pick movie card tied to Rafael’s dark fantasy and superhero taste profile.")

    for p, t in files:
        if "ai consensus system project" in p.name.lower() and "daily insights" in t.lower():
            ideas.append("Bring back the 30-second daily insight concept as the top section of the agent summary digest.")
            break

    return dedupe(ideas)[:10]


def build_digest(files: List[Tuple[Path, str]], pred_items: List[dict], snapshot_rows: List[dict], source_root: Path) -> str:
    now = datetime.now(timezone.utc).isoformat()
    rel_docs = top_relevant_docs(files)
    warn_count = sum(1 for r in snapshot_rows if r["status"].lower() == "warn")

    lines = [
        "# Agent Summary Digest",
        f"- Generated: {now}",
        f"- Agent: current_project_agent_digest.py {VERSION}",
        f"- Source root: {source_root}",
        "",
        "## What this layer is for",
        "This digest restores the old agent_summaries purpose using the current project: human-readable brainstorming, optimization, and suggestion output on top of the operational logs.",
        "",
        "## Current read of the project",
        f"- Prediction items parsed: {len(pred_items)}",
        f"- Health snapshot subsystems parsed: {len(snapshot_rows)}",
        f"- Warning subsystems: {warn_count}",
        "",
        "## Highest-signal findings",
    ]

    if pred_items:
        for item in pred_items[:8]:
            lines.append(f"- [{item['severity']}] {item['section']}: {item['message']}")
    else:
        lines.append("- No prediction feed items were parsed from the latest prediction feed file.")

    if snapshot_rows:
        lines.extend(["", "## Stale or warning subsystems"])
        warned = False
        for row in snapshot_rows:
            if row["status"].lower() == "warn":
                warned = True
                lines.append(f"- {row['subsystem']}: {row['notes']}")
        if not warned:
            lines.append("- No warning subsystems were found in the latest health snapshot.")

    lines.extend(["", "## Most relevant source files used in this run"])
    for p in rel_docs:
        lines.append(f"- {p}")

    return "\n".join(lines) + "\n"


def write_list(path: Path, title: str, items: List[str]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        f"# {title}",
        f"- Generated: {now}",
        f"- Agent: current_project_agent_digest.py {VERSION}",
        "",
    ]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    source_root = Path(args.source_root)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    files = collect_docs(source_root)
    pred_text = latest_prediction_text(files)
    snapshot_text = latest_snapshot_text(files)
    pred_items = parse_prediction_items(pred_text)
    snapshot_rows = parse_snapshot(snapshot_text)

    today = datetime.now().strftime("%Y-%m-%d_0905")

    digest = build_digest(files, pred_items, snapshot_rows, source_root)
    (out_dir / f"agent_summary_digest_{today}.md").write_text(digest, encoding="utf-8")

    write_list(
        out_dir / f"top10_suggestions_{today}.md",
        "Top 10 Suggestions",
        build_suggestions(pred_items, files),
    )
    write_list(
        out_dir / f"top10_optimizations_{today}.md",
        "Top 10 Optimizations",
        build_optimizations(snapshot_rows, files),
    )
    write_list(
        out_dir / f"top10_brainstorm_{today}.md",
        "Top 10 Brainstorm",
        build_brainstorm(files, pred_items, snapshot_rows),
    )

    summary = {
        "source_files": len(files),
        "prediction_items": len(pred_items),
        "snapshot_rows": len(snapshot_rows),
        "out_dir": str(out_dir),
    }
    (out_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())