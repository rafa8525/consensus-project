import unittest
from milestone22_confirmation import (SEEDS,FAMILIES,BASELINE,CANDIDATE,
                                      grid_for,score,validate_specs)
from milestone20_planner import bounded_search
from milestone21_robustness import oracle_relaxation
from solo_vs_team_planning import GRID_SIZE

class PreregisteredConfirmationTests(unittest.TestCase):
    def test_case_count(self):
        self.assertEqual(len(SEEDS)*len(FAMILIES),192)
    def test_frozen_set(self):
        with self.assertRaises(PermissionError):
            validate_specs(BASELINE,dict(CANDIDATE,weight=1.25))
    def test_disallowed_seed(self):
        with self.assertRaises(ValueError):grid_for(FAMILIES[0],61000)
    def test_grid_determinism(self):
        self.assertEqual(grid_for(FAMILIES[0],73000),grid_for(FAMILIES[0],73000))
    def test_all_families_differ(self):
        self.assertEqual(len({grid_for(f,73000) for f in FAMILIES}),4)
    def test_all_family_paths_valid(self):
        for family in FAMILIES:
            for seed in SEEDS[:3]:
                self.assertIsNotNone(oracle_relaxation(grid_for(family,seed)))
    def test_oracle_baseline_consistency(self):
        for family in FAMILIES:
            for seed in SEEDS[:3]:
                g=grid_for(family,seed)
                self.assertEqual(bounded_search(g,BASELINE)["cost"],oracle_relaxation(g))
    def test_report_reproducible_without_latency(self):
        self.assertEqual(score(latency=False),score(latency=False))
    def test_no_promotion(self):
        report=score(latency=False)
        self.assertFalse(report["promotion_approved"])
        self.assertFalse(report["external_protected_holdout"])
        self.assertEqual(report["live_model_calls"],0)
    def test_primary_gate_matches_count(self):
        report=score(latency=False)
        self.assertEqual(report["primary_correctness_pass"],
                         report["optimal_candidate_total"]==192)
    def test_timing_optional(self):
        report=score(latency=False)
        self.assertIsNone(report["families"]["zigzag_corridor"]["latency_median_ns"])
if __name__=="__main__":unittest.main()
