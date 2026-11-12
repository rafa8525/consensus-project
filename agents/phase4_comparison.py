"""Phase 4 deterministic comparison of bounded offline improvement candidates.

This ranks only synthetic, independently supplied metric fixtures; it cannot
execute a candidate, change code or authorize deployment.
"""
from agents.phase4_evaluator import evaluate_fixture, EvaluationError

def compare_candidates(baseline, candidates, *, now=None, simulation=False):
    if simulation is not True:
        raise EvaluationError("explicit simulation=True required")
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 8:
        raise EvaluationError("1-8 candidates required")
    decisions = []
    seen = set()
    for entry in candidates:
        if not isinstance(entry, dict) or set(entry) != {"proposal", "measurement"}:
            raise EvaluationError("invalid candidate entry")
        proposal = entry["proposal"]
        if not isinstance(proposal, dict) or not isinstance(proposal.get("id"), str):
            raise EvaluationError("candidate ID required")
        if proposal["id"] in seen:
            raise EvaluationError("duplicate candidate ID")
        seen.add(proposal["id"])
        report = evaluate_fixture(
            {"baseline": baseline, "candidate": entry["measurement"],
             "proposal": proposal}, now=now, simulation=True)
        decisions.append({"id": proposal["id"], "decision": report["decision"],
                          "reasons": report["reasons"],
                          "candidate_sha": report["candidate_sha"],
                          "latency_ms": entry["measurement"]["metrics"]["latency_ms"],
                          "resource_units": entry["measurement"]["metrics"]["resource_units"]})
    eligible = [x for x in decisions if x["decision"] == "ELIGIBLE_FOR_REVIEW"]
    eligible.sort(key=lambda x: (x["latency_ms"], x["resource_units"], x["id"]))
    return {"candidates": decisions,
            "review_priority": [x["id"] for x in eligible],
            "deployment_allowed": False,
            "evidence_type": "synthetic-self-reported-not-independent"}
