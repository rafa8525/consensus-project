"""Phase 4 deterministic proposal generation and evaluator integration."""
import unittest
from datetime import datetime, timezone
from agents.phase4_candidates import generate_and_score
from agents.phase4_evaluator import EvaluationError

NOW = datetime(2026, 11, 12, 22, 0, tzinfo=timezone.utc)
A = "a" * 40
B = "b" * 40

def run(requests):
    return generate_and_score(
        requests, baseline_sha=A, candidate_sha=B, now=NOW, simulation=True)

class CandidateTests(unittest.TestCase):
    def test_duplicate_side_effect_suppressed_without_rerun(self):
        items = [{"task_id": "one", "duration_ms": 20, "side_effect": True},
                 {"task_id": "one", "duration_ms": 20, "side_effect": True},
                 {"task_id": "two", "duration_ms": 5, "side_effect": False}]
        result = run(items)
        self.assertEqual(result["decision"]["decision"], "ELIGIBLE_FOR_REVIEW")
        self.assertFalse(result["decision"]["deployment_allowed"])
        self.assertEqual(result["measurements"]["baseline"]["duplicate_effects"], 1)
        self.assertEqual(result["measurements"]["candidate"]["duplicate_effects"], 0)
        self.assertLess(result["measurements"]["candidate"]["latency_ms"],
                        result["measurements"]["baseline"]["latency_ms"])

    def test_no_duplicates_yields_no_unfounded_claim(self):
        items = [{"task_id": "one", "duration_ms": 5, "side_effect": True}]
        result = run(items)
        self.assertEqual(result["measurements"]["baseline"],
                         result["measurements"]["candidate"])
        self.assertEqual(result["decision"]["evidence_type"],
                         "synthetic-self-reported-not-independent")

    def test_deterministic_metrics(self):
        items = [{"task_id": "a", "duration_ms": 7, "side_effect": False},
                 {"task_id": "a", "duration_ms": 7, "side_effect": False}]
        self.assertEqual(run(items), run(items))

    def test_reject_invalid_fixture(self):
        invalid = [
            [],
            [{"task_id": "bad id", "duration_ms": 5, "side_effect": False}],
            [{"task_id": "one", "duration_ms": -1, "side_effect": False}],
            [{"task_id": "one", "duration_ms": 1, "side_effect": 1}],
            [{"task_id": "one", "duration_ms": 1, "side_effect": True, "extra": 1}],
        ]
        for items in invalid:
            with self.subTest(items=items), self.assertRaises(EvaluationError):
                run(items)

    def test_invalid_candidate_sha_rejected(self):
        with self.assertRaises(EvaluationError):
            generate_and_score(
                [{"task_id": "a", "duration_ms": 4, "side_effect": True}],
                baseline_sha=A, candidate_sha="bad", now=NOW, simulation=True)

    def test_simulation_required(self):
        with self.assertRaises(EvaluationError):
            generate_and_score(
                [{"task_id": "a", "duration_ms": 4, "side_effect": True}],
                baseline_sha=A, candidate_sha=B, now=NOW)

if __name__ == "__main__":
    unittest.main()
