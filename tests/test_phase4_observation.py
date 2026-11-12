"""Fail closed on missing, conflicting, or unbound simulated observations."""
import copy
from datetime import datetime,timezone
import unittest
from agents.phase4_observation import evaluate_observed
from agents.phase4_evaluator import EvaluationError
from tests.test_phase4_evaluator import case, NOW

def observations(fixture):
    return {side: {
        "fixture_id":fixture[side]["fixture_id"],
        "commit_sha":fixture[side]["commit_sha"],
        "sample_count":fixture[side]["sample_count"],
        "metrics":dict(fixture[side]["metrics"]),
        "observer_id":"offline-test-harness-v1",
    } for side in ("baseline","candidate")}

class ObservationTests(unittest.TestCase):
    def test_matching_harness_reaches_review_only(self):
        f=case();f["candidate"]["metrics"]["latency_ms"]=80
        r=evaluate_observed(f,observations(f),now=NOW,simulation=True)
        self.assertEqual(r["decision"],"ELIGIBLE_FOR_REVIEW")
        self.assertFalse(r["deployment_allowed"])
    def test_missing_observation_rejected(self):
        f=case();o=observations(f);del o["candidate"]
        with self.assertRaises(EvaluationError):
            evaluate_observed(f,o,now=NOW,simulation=True)
    def test_synthetic_self_report_mismatch_rejected(self):
        f=case();o=observations(f)
        f["candidate"]["metrics"]["latency_ms"]=1
        with self.assertRaises(EvaluationError):
            evaluate_observed(f,o,now=NOW,simulation=True)
    def test_wrong_commit_and_fixture_rejected(self):
        for key,val in (("commit_sha","c"*40),("fixture_id","other"),("sample_count",99)):
            f=case();o=observations(f);o["candidate"][key]=val
            with self.subTest(key=key),self.assertRaises(EvaluationError):
                evaluate_observed(f,o,now=NOW,simulation=True)
    def test_observer_spoofing_rejected(self):
        f=case();o=observations(f);o["candidate"]["observer_id"]="candidate-self-report"
        with self.assertRaises(EvaluationError):
            evaluate_observed(f,o,now=NOW,simulation=True)
    def test_safety_regression_still_rejected(self):
        f=case();f["candidate"]["metrics"]["unauthorized_writes"]=1
        r=evaluate_observed(f,observations(f),now=NOW,simulation=True)
        self.assertEqual(r["decision"],"REJECTED")
    def test_explicit_simulation_required(self):
        f=case()
        with self.assertRaises(EvaluationError):
            evaluate_observed(f,observations(f),now=NOW)
if __name__=="__main__": unittest.main()
