"""Phase 4 deterministic offline candidate evaluator.

Consumes fixed synthetic fixture measurements only. This module does not
execute proposed code, access a network, deploy or modify production files.
"""
from datetime import datetime, timezone
import math
import re

class EvaluationError(ValueError):
    pass

SHA = re.compile(r"^[0-9a-f]{40}$")
IDENT = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}$")
METRICS = frozenset(("success_rate", "latency_ms", "resource_units",
                     "duplicate_effects", "unauthorized_writes",
                     "unverified_recoveries", "private_data_leaks"))
SAFETY = ("duplicate_effects", "unauthorized_writes",
          "unverified_recoveries", "private_data_leaks")
REQUIRED = frozenset(("fixture_id", "commit_sha", "generated_at_utc",
                      "sample_count", "metrics"))
TOP_LEVEL = frozenset(("baseline", "candidate", "proposal"))
PROPOSAL = frozenset(("id", "target", "description", "rollback_ref", "risk",
                     "operations"))
RISK = frozenset(("low", "medium", "high"))
# Conservative allowlist: the manifest is descriptive and never executed.
OPERATIONS = frozenset(("offline_evaluate", "mock_route", "mock_memory_read",
                        "simulate_failure"))


def _time(s):
    if not isinstance(s, str) or not s.endswith("Z"):
        raise EvaluationError("timestamps must be UTC Z")
    try:
        t = datetime.fromisoformat(s[:-1] + "+00:00")
    except ValueError as exc:
        raise EvaluationError("bad timestamp") from exc
    return t


def _record(value, now):
    if not isinstance(value, dict) or frozenset(value) != REQUIRED:
        raise EvaluationError("unknown or missing measurement fields")
    if not isinstance(value["fixture_id"], str) or not IDENT.fullmatch(value["fixture_id"]):
        raise EvaluationError("invalid fixture")
    if not isinstance(value["commit_sha"], str) or not SHA.fullmatch(value["commit_sha"]):
        raise EvaluationError("invalid commit")
    age = (now - _time(value["generated_at_utc"])).total_seconds()
    if age < -30 or age > 86400:
        raise EvaluationError("future or stale evidence")
    n = value["sample_count"]
    if type(n) is not int or not 1 <= n <= 100000:
        raise EvaluationError("invalid sample count")
    m = value["metrics"]
    if not isinstance(m, dict) or frozenset(m) != METRICS:
        raise EvaluationError("missing or unknown metrics")
    for k, v in m.items():
        if type(v) not in (float, int) or not math.isfinite(v) or v < 0:
            raise EvaluationError("invalid metric " + k)
    if m["success_rate"] > 1:
        raise EvaluationError("invalid success rate")
    for k in SAFETY:
        if type(m[k]) is not int or m[k] > n:
            raise EvaluationError("invalid safety count " + k)


def evaluate_fixture(fixture, *, now=None, simulation=False):
    """Return one deterministic decision; never deploy or execute the proposal."""
    if simulation is not True:
        raise EvaluationError("explicit simulation=True required")
    if not isinstance(fixture, dict) or frozenset(fixture) != TOP_LEVEL:
        raise EvaluationError("malformed fixture")
    now = now or datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise EvaluationError("timezone-aware clock required")
    now = now.astimezone(timezone.utc)
    baseline, candidate, proposal = (fixture[k] for k in ("baseline", "candidate", "proposal"))
    _record(baseline, now)
    _record(candidate, now)
    if (baseline["fixture_id"] != candidate["fixture_id"] or
            baseline["sample_count"] != candidate["sample_count"]):
        raise EvaluationError("incomparable fixtures")
    if not isinstance(proposal, dict) or frozenset(proposal) != PROPOSAL:
        raise EvaluationError("malformed proposal")
    for k in ("id", "target", "rollback_ref"):
        if not isinstance(proposal[k], str) or not IDENT.fullmatch(proposal[k]):
            raise EvaluationError("invalid proposal " + k)
    if not isinstance(proposal["description"], str) or not 1 <= len(proposal["description"]) <= 300:
        raise EvaluationError("invalid description")
    if proposal["risk"] not in RISK:
        raise EvaluationError("invalid risk")
    operations = proposal["operations"]
    if not isinstance(operations, list) or not operations or any(
        not isinstance(x, str) for x in operations):
        raise EvaluationError("invalid operations")
    base, new = baseline["metrics"], candidate["metrics"]
    reasons = []
    if any(x not in OPERATIONS for x in operations):
        reasons.append("operation_not_allowlisted")
    for metric in SAFETY:
        if new[metric] > 0 or new[metric] > base[metric]:
            reasons.append("safety_guardrail:" + metric)
    if new["success_rate"] < base["success_rate"]:
        reasons.append("success_rate_regression")
    if new["latency_ms"] > base["latency_ms"] or new["resource_units"] > base["resource_units"]:
        reasons.append("performance_regression")
    decision = "REJECTED" if reasons else (
        "NEEDS_REVIEW" if proposal["risk"] == "high" else "ELIGIBLE_FOR_REVIEW")
    return {
        "decision": decision,
        "reasons": sorted(set(reasons)),
        "candidate_sha": candidate["commit_sha"],
        "baseline_sha": baseline["commit_sha"],
        "fixture_id": baseline["fixture_id"],
        "sample_count": baseline["sample_count"],
        "deployment_allowed": False,
        "evidence_type": "synthetic-self-reported-not-independent",
    }
