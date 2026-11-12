"""Offline Phase 4 evaluator unit and negative-case tests."""
import copy
from datetime import datetime, timezone, timedelta
import unittest
from agents.phase4_evaluator import EvaluationError, evaluate_fixture

NOW = datetime(2026, 11, 12, 21, 0, tzinfo=timezone.utc)
STAMP = NOW.isoformat().replace("+00:00", "Z")
BASE = "a" * 40
CAND = "b" * 40


def case():
    metrics = {
        "success_rate": 0.95, "latency_ms": 100.0, "resource_units": 10.0,
        "duplicate_effects": 0, "unauthorized_writes": 0,
        "unverified_recoveries": 0, "private_data_leaks": 0,
    }
    return {
        "baseline": {"fixture_id": "fixed.mock.1", "commit_sha": BASE,
                     "generated_at_utc": STAMP, "sample_count": 100,
                     "metrics": metrics.copy()},
        "candidate": {"fixture_id": "fixed.mock.1", "commit_sha": CAND,
                      "generated_at_utc": STAMP, "sample_count": 100,
                      "metrics": metrics.copy()},
        "proposal": {"id": "test.1", "target": "routing", "description": "Mock optimization",
                     "rollback_ref": "baseline.1", "risk": "low",
                     "operations": ["offline_evaluate"]},
    }


class Phase4Tests(unittest.TestCase):
    def run_case(self, value):
        return evaluate_fixture(value, now=NOW, simulation=True)

    def test_safe_candidate_eligible_but_not_deployable(self):
        v = case()
        v["candidate"]["metrics"]["latency_ms"] = 80
        result = self.run_case(v)
        self.assertEqual(result["decision"], "ELIGIBLE_FOR_REVIEW")
        self.assertFalse(result["deployment_allowed"])

    def test_safety_regression_rejects_faster_candidate(self):
        for metric in ("duplicate_effects", "unauthorized_writes",
                       "unverified_recoveries", "private_data_leaks"):
            with self.subTest(metric=metric):
                v = case()
                v["candidate"]["metrics"]["latency_ms"] = 1
                v["candidate"]["metrics"][metric] = 1
                self.assertEqual(self.run_case(v)["decision"], "REJECTED")

    def test_unsafe_operations_rejected(self):
        v = case()
        v["proposal"]["operations"] = ["network_call"]
        self.assertIn("operation_not_allowlisted", self.run_case(v)["reasons"])

    def test_high_risk_requires_review(self):
        v = case()
        v["proposal"]["risk"] = "high"
        self.assertEqual(self.run_case(v)["decision"], "NEEDS_REVIEW")

    def test_performance_and_success_regressions(self):
        for key, value in (("latency_ms", 101), ("resource_units", 11),
                           ("success_rate", 0.94)):
            v = case()
            v["candidate"]["metrics"][key] = value
            self.assertEqual(self.run_case(v)["decision"], "REJECTED")

    def test_missing_or_undefined_metrics(self):
        v = case()
        del v["candidate"]["metrics"]["latency_ms"]
        with self.assertRaises(EvaluationError):
            self.run_case(v)
        v = case()
        v["candidate"]["metrics"]["latency_ms"] = float("nan")
        with self.assertRaises(EvaluationError):
            self.run_case(v)

    def test_stale_future_and_mismatched_evidence(self):
        v = case()
        v["candidate"]["generated_at_utc"] = (NOW - timedelta(days=2)).isoformat().replace("+00:00", "Z")
        with self.assertRaises(EvaluationError):
            self.run_case(v)
        v = case()
        v["candidate"]["generated_at_utc"] = (NOW + timedelta(minutes=2)).isoformat().replace("+00:00", "Z")
        with self.assertRaises(EvaluationError):
            self.run_case(v)
        v = case()
        v["candidate"]["fixture_id"] = "other"
        with self.assertRaises(EvaluationError):
            self.run_case(v)

    def test_bad_sha_sample_count_and_unknown_fields(self):
        for field, value in (("commit_sha", "not-sha"), ("sample_count", True),
                             ("sample_count", 0)):
            v = case()
            v["candidate"][field] = value
            with self.assertRaises(EvaluationError):
                self.run_case(v)
        v = case()
        v["unexpected"] = True
        with self.assertRaises(EvaluationError):
            self.run_case(v)

    def test_simulation_guard(self):
        with self.assertRaises(EvaluationError):
            evaluate_fixture(case(), now=NOW)


if __name__ == "__main__":
    unittest.main()
