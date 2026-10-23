#!/usr/bin/env python3
"""Evidence-only ACS-01..05 baseline. Read-only; no claims of learned intelligence."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

AGENTS = ("ACS-01", "ACS-02", "ACS-03", "ACS-04", "ACS-05")
METRIC_CAP = 20000

def _metric_rows(path: Path):
    try:
        with path.open(encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                if index >= METRIC_CAP:
                    break
                try:
                    item = json.loads(line)
                    if isinstance(item, dict):
                        yield item
                except (ValueError, TypeError):
                    continue
    except OSError:
        return

def evaluate(repo: Path) -> dict:
    state_dir = repo / "memory/agents"
    source = state_dir / "state.json"
    result = {"source": str(source), "agents": {}, "sample_limit": METRIC_CAP}
    try:
        state = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            raise ValueError("not a JSON object")
    except (OSError, ValueError, TypeError):
        state = {}
    supervisor_results = state.get("last_supervisor_results", {})
    if not isinstance(supervisor_results, dict):
        supervisor_results = {}
    supervisor_ok = state.get("last_supervisor_status") == "ok" and bool(supervisor_results)
    result["agents"]["ACS-01"] = {
        "observed": bool(supervisor_results),
        "latest_status": state.get("last_supervisor_status", "unknown") if supervisor_results else "unknown",
        "latest_healthy": supervisor_ok if supervisor_results else None,
        "last_timestamp": state.get("last_supervisor_ts") if supervisor_results else None,
        "historical_success_rate": None,
    }
    for agent in AGENTS[1:]:
        key = agent.lower().replace("-", "_")
        entry = supervisor_results.get(key)
        if not isinstance(entry, dict):
            result["agents"][agent] = {"observed": False, "latest_status": "unknown",
                                       "latest_healthy": None, "historical_success_rate": None}
            continue
        result["agents"][agent] = {
            "observed": True,
            "latest_status": entry.get("status", "unknown"),
            "latest_healthy": entry.get("ok") is True and entry.get("status") == "healthy",
            "attempt_count": entry.get("attempt_count"),
            "historical_success_rate": None,
        }
    metrics = repo / "memory/logs/agents/metrics.jsonl"
    counts = {"supervisor_success": 0, "supervisor_degraded": 0, "other": 0, "malformed": 0}
    try:
        # Bound runtime and avoid loading entire large log into memory.
        with metrics.open(encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                if index >= METRIC_CAP:
                    break
                try:
                    event = json.loads(line)
                    if event.get("metric") != "supervisor_cycle":
                        counts["other"] += 1
                    elif event.get("status") == "ok":
                        counts["supervisor_success"] += 1
                    elif event.get("status") == "degraded":
                        counts["supervisor_degraded"] += 1
                    else:
                        counts["malformed"] += 1
                except (ValueError, AttributeError):
                    counts["malformed"] += 1
    except OSError:
        pass
    n = counts["supervisor_success"] + counts["supervisor_degraded"]
    result["supervisor_metric_history"] = {
        "observed_cycles": n,
        "successes": counts["supervisor_success"],
        "degraded": counts["supervisor_degraded"],
        "unknown_or_invalid": counts["malformed"],
        "success_rate": round(counts["supervisor_success"] / n, 4) if n else None,
        "scope": "supervisor cycles only, up to first 20000 metric rows; not per-agent learning",
    }
    # Outcome history begins when the per-agent metric was first recorded.
    # Do not backfill child outcomes from aggregate supervisor metrics.
    per_agent = {agent: {"observations": 0, "healthy": 0, "degraded": 0, "success_rate": None}
                 for agent in AGENTS}
    for event in _metric_rows(metrics):
        if event.get("metric") != "agent_cycle_outcome":
            continue
        agent = event.get("agent")
        if agent not in per_agent:
            continue
        status = event.get("status")
        if status not in ("healthy", "degraded", "warning", "critical", "execution_failure"):
            continue
        row = per_agent[agent]
        row["observations"] += 1
        if status == "healthy":
            row["healthy"] += 1
        else:
            row["degraded"] += 1
    for row in per_agent.values():
        if row["observations"]:
            row["success_rate"] = round(row["healthy"] / row["observations"], 4)
    result["per_agent_metric_history"] = per_agent
    result["learning_effectiveness_verified"] = False
    result["note"] = "A healthy execution or artifact is not evidence of decision learning. Historical agent rates require per-cycle measurements."
    return result

def simulated_promotion_gate(snapshot: dict) -> tuple[bool, str]:
    """Conservative all-five deployment check. Does not deploy or edit files."""
    agents = snapshot.get("agents", {})
    if any(not isinstance(agents.get(agent), dict)
           or agents[agent].get("latest_healthy") is not True
           for agent in AGENTS):
        return False, "one or more ACS-01..05 agents unverified or unhealthy"
    return True, "all five latest statuses healthy; NOT proof of learning improvement"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.home() / "consensus-project")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.repo), indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
