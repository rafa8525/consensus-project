"""Deterministic Phase 4 mock policy generator and evaluation runner.

This never generates executable code or touches live agents. It evaluates a
bounded, fixed synthetic request fixture for duplicate suppression policies.
"""
from datetime import datetime, timezone
from agents.phase4_evaluator import EvaluationError, evaluate_fixture

def _measure(requests, *, suppress_duplicates):
    seen = set()
    success = 0
    duplicate_effects = 0
    latency = 0
    resource = 0
    for item in requests:
        if item["task_id"] in seen and suppress_duplicates:
            # Synthetic cached result is counted as a successful response.
            success += 1
            continue
        if item["task_id"] in seen and item["side_effect"]:
            duplicate_effects += 1
        seen.add(item["task_id"])
        success += 1
        latency += item["duration_ms"]
        resource += 1
    return {
        "success_rate": success / len(requests),
        "latency_ms": float(latency),
        "resource_units": float(resource),
        "duplicate_effects": duplicate_effects,
        "unauthorized_writes": 0,
        "unverified_recoveries": 0,
        "private_data_leaks": 0,
    }


def generate_and_score(requests, *, baseline_sha, candidate_sha,
                       now=None, simulation=False):
    """Generate mock de-duplication proposal and score against the same inputs."""
    if simulation is not True:
        raise EvaluationError("explicit simulation=True required")
    if not isinstance(requests, list) or not 1 <= len(requests) <= 100:
        raise EvaluationError("1-100 synthetic requests required")
    ids = set()
    for item in requests:
        if not isinstance(item, dict) or set(item) != {
            "task_id", "duration_ms", "side_effect"
        }:
            raise EvaluationError("malformed synthetic request")
        ident = item["task_id"]
        if not isinstance(ident, str) or not ident or len(ident) > 80 or not all(
            x.isalnum() or x in "._-" for x in ident
        ):
            raise EvaluationError("invalid task identifier")
        if type(item["duration_ms"]) is not int or not 1 <= item["duration_ms"] <= 10000:
            raise EvaluationError("invalid mock duration")
        if type(item["side_effect"]) is not bool:
            raise EvaluationError("invalid side-effect flag")
        ids.add(ident)
    now = now or datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise EvaluationError("aware time required")
    stamp = now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    fixture_id = "mock-routing-dedupe-v1"
    records = []
    for sha, dedupe in ((baseline_sha, False), (candidate_sha, True)):
        records.append({
            "fixture_id": fixture_id,
            "commit_sha": sha,
            "generated_at_utc": stamp,
            "sample_count": len(requests),
            "metrics": _measure(requests, suppress_duplicates=dedupe),
        })
    fixture = {
        "baseline": records[0], "candidate": records[1],
        "proposal": {
            "id": "dedupe.v1", "target": "routing",
            "description": "Suppress duplicate synthetic task execution",
            "rollback_ref": "baseline.v1", "risk": "low",
            "operations": ["mock_route", "offline_evaluate"],
        },
    }
    report = evaluate_fixture(fixture, now=now, simulation=True)
    return {"proposal": fixture["proposal"], "measurements": {
        "baseline": records[0]["metrics"], "candidate": records[1]["metrics"]
    }, "decision": report}
