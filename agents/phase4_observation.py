"""Phase 4 independent *mock* observation gate.

Unlike candidate-supplied metrics, observer records come from a separately
injected offline harness. The module checks exact fixture/sample identity and
metric agreement. No real-world independence or attestation is claimed.
"""
import math
from agents.phase4_evaluator import EvaluationError, METRICS, evaluate_fixture

def evaluate_observed(fixture, observations, *, now=None, simulation=False):
    if simulation is not True:
        raise EvaluationError("simulation=True required")
    if not isinstance(observations,dict) or set(observations)!={"baseline","candidate"}:
        raise EvaluationError("both independent mock observations required")
    for side in ("baseline","candidate"):
        record=fixture.get(side) if isinstance(fixture,dict) else None
        observed=observations[side]
        if not isinstance(record,dict) or not isinstance(observed,dict):
            raise EvaluationError("invalid observation")
        if set(observed)!={"fixture_id","commit_sha","sample_count","metrics","observer_id"}:
            raise EvaluationError("observation fields mismatch")
        if observed["fixture_id"]!=record.get("fixture_id") or observed["commit_sha"]!=record.get("commit_sha") or observed["sample_count"]!=record.get("sample_count"):
            raise EvaluationError("unmatched observation")
        if observed["observer_id"]!="offline-test-harness-v1":
            raise EvaluationError("untrusted mock observer")
        metrics=observed["metrics"]
        if not isinstance(metrics,dict) or set(metrics)!=METRICS:
            raise EvaluationError("invalid observer metrics")
        for metric in METRICS:
            claimed=record.get("metrics",{}).get(metric)
            value=metrics[metric]
            if type(value) not in (int,float) or not math.isfinite(value) or value != claimed:
                raise EvaluationError("observer disagrees with candidate claim")
    report=evaluate_fixture(fixture,now=now,simulation=True)
    return dict(report, evidence_type="cross-checked-synthetic-harness-only",
                observer="offline-test-harness-v1")
