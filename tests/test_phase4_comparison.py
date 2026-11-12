"""Multi-candidate ranking, guardrails, deterministic ties and bad evidence."""
from datetime import datetime, timezone
import copy
import unittest
from agents.phase4_comparison import compare_candidates
from agents.phase4_evaluator import EvaluationError

NOW = datetime(2026, 11, 12, 22, 0, tzinfo=timezone.utc)
STAMP = NOW.isoformat().replace("+00:00", "Z")
BASE = {"success_rate": 1.0, "latency_ms": 100.0, "resource_units": 10.0,
        "duplicate_effects": 0, "unauthorized_writes": 0,
        "unverified_recoveries": 0, "private_data_leaks": 0}

def measurement(sha, **updates):
    metrics = dict(BASE)
    metrics.update(updates)
    return {"fixture_id": "fixed.v1", "commit_sha": sha * 40,
            "generated_at_utc": STAMP, "sample_count": 100, "metrics": metrics}

def candidate(name, sha, risk="low", **metrics):
    return {"proposal": {"id": name, "target": "routing",
                         "description": "Synthetic improvement",
                         "rollback_ref": "baseline.v1", "risk": risk,
                         "operations": ["offline_evaluate"]},
            "measurement": measurement(sha, **metrics)}

def run(candidates):
    return compare_candidates(measurement("a"), candidates, now=NOW, simulation=True)

class ComparisonTests(unittest.TestCase):
    def test_rank_safe_candidates_with_deterministic_tie(self):
        items = [candidate("slow", "b", latency_ms=90),
                 candidate("fast", "c", latency_ms=70),
                 candidate("tie", "d", latency_ms=70, resource_units=9)]
        result = run(items)
        self.assertEqual(result["review_priority"], ["tie", "fast", "slow"])
        self.assertFalse(result["deployment_allowed"])

    def test_reject_faster_unsafe_candidate(self):
        result = run([candidate("unsafe", "b", latency_ms=1, unauthorized_writes=1),
                      candidate("safe", "c", latency_ms=80)])
        self.assertEqual(result["review_priority"], ["safe"])
        self.assertEqual(result["candidates"][0]["decision"], "REJECTED")

    def test_high_risk_not_eligible_for_priority(self):
        result = run([candidate("higher", "b", risk="high", latency_ms=1),
                      candidate("lower", "c", latency_ms=80)])
        self.assertEqual(result["review_priority"], ["lower"])
        self.assertEqual(result["candidates"][0]["decision"], "NEEDS_REVIEW")

    def test_duplicate_id_rejected(self):
        with self.assertRaises(EvaluationError):
            run([candidate("same", "b"), candidate("same", "c")])

    def test_incomparable_fixture_rejected(self):
        bad = candidate("broken", "b")
        bad["measurement"]["sample_count"] = 99
        with self.assertRaises(EvaluationError):
            run([bad])

    def test_missing_or_excessive_candidates_rejected(self):
        with self.assertRaises(EvaluationError):
            run([])
        with self.assertRaises(EvaluationError):
            run([candidate("c" + str(i), "b") for i in range(9)])

    def test_explicit_simulation_required(self):
        with self.assertRaises(EvaluationError):
            compare_candidates(measurement("a"), [candidate("a", "b")], now=NOW)

if __name__ == "__main__":
    unittest.main()
