#!/usr/bin/env python3
"""Read-only, evidence-linked historical learning effectiveness assessment.

Operational success rates are NOT learning. A learning improvement may be
supported only by comparable before/after evaluations with a documented change,
independent immutable evidence files, and sufficient samples. The tool never
claims causation or rewrites earlier history.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

AGENTS = {"ACS-01", "ACS-02", "ACS-03", "ACS-04", "ACS-05"}
MIN_SAMPLES = 3
MAX_ROWS = 20000

def read_events(path: Path):
    try:
        with path.open(encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                if index >= MAX_ROWS:
                    break
                try:
                    event = json.loads(line)
                    if isinstance(event, dict):
                        yield event
                except (ValueError, TypeError):
                    continue
    except OSError:
        return

def verify_evidence(repo: Path, row: dict) -> bool:
    name = row.get("evidence_path")
    digest = row.get("evidence_sha256")
    if not isinstance(name, str) or not name or not isinstance(digest, str) or len(digest) != 64:
        return False
    # Only immutable, existing, repository-relative evidence; no traversal or symlinks.
    candidate = repo / name
    try:
        if candidate.is_symlink() or not candidate.is_file() or candidate.stat().st_size > 1024 * 1024:
            return False
        if repo.resolve() not in candidate.resolve().parents:
            return False
        if not name.startswith("memory/logs/agents/learning_evidence/"):
            return False
        return hashlib.sha256(candidate.read_bytes()).hexdigest() == digest
    except OSError:
        return False

def assess(repo: Path) -> dict:
    groups = defaultdict(lambda: {"before": [], "after": [], "rejected": 0})
    rows = repo / "memory/logs/agents/learning_evaluations.jsonl"
    for row in read_events(rows):
        agent = row.get("agent")
        change = row.get("change_id")
        scenario = row.get("scenario_id")
        phase = row.get("phase")
        passed = row.get("passed")
        if (agent not in AGENTS or not isinstance(change, str) or not change
            or not isinstance(scenario, str) or not scenario
            or phase not in ("before", "after") or type(passed) is not bool):
            continue
        key = (agent, change, scenario)
        if verify_evidence(repo, row):
            groups[key][phase].append(int(passed))
        else:
            groups[key]["rejected"] += 1
    assessments = []
    for (agent, change, scenario), data in sorted(groups.items()):
        before = data["before"]
        after = data["after"]
        enough = len(before) >= MIN_SAMPLES and len(after) >= MIN_SAMPLES
        b_rate = sum(before) / len(before) if before else None
        a_rate = sum(after) / len(after) if after else None
        improved = bool(enough and a_rate > b_rate)
        assessments.append({
            "agent": agent, "change_id": change, "scenario_id": scenario,
            "before_samples": len(before), "after_samples": len(after),
            "before_pass_rate": round(b_rate, 4) if b_rate is not None else None,
            "after_pass_rate": round(a_rate, 4) if a_rate is not None else None,
            "evidence_rejected": data["rejected"],
            "observed_improvement_supported": improved,
            "status": "observed_improvement" if improved else ("no_improvement_observed" if enough else "insufficient_evidence"),
        })
    supported = [x for x in assessments if x["observed_improvement_supported"]]
    return {
        "evaluated_scenarios": len(assessments),
        "observed_improvement_scenarios": len(supported),
        "learning_effectiveness_verified": bool(supported),
        "assessments": assessments,
        "limits": ("Same-scenario evidence-linked pre/post comparisons only. "
                   "Observational improvement does not establish causation, "
                   "general learning, or independent agent intelligence. "
                   "Prior evidence cannot be reconstructed from aggregate health logs."),
        "read_only": True,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.home() / "consensus-project")
    args = parser.parse_args()
    print(json.dumps(assess(args.repo), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
