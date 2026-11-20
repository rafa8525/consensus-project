import unittest
from milestone21_robustness import (FAMILIES,SEEDS,create_case,oracle_relaxation,
                                   fixed_specs,evaluate)
from milestone20_planner import bounded_search
from solo_vs_team_planning import GRID_SIZE

class M21Robustness(unittest.TestCase):
    def test_seed_count(self):
        self.assertEqual(len(SEEDS),64)
        self.assertEqual(len(FAMILIES),4)
    def test_reproducibility(self):
        for f in FAMILIES:
            self.assertEqual(create_case(f,61000),create_case(f,61000))
    def test_novel_family(self):
        self.assertNotEqual(create_case(FAMILIES[1],61000),
                            create_case(FAMILIES[2],61000))
    def test_guaranteed_path(self):
        for f in FAMILIES:
            self.assertIsNotNone(oracle_relaxation(create_case(f,61000)))
    def test_oracle_tiny_easy_grid(self):
        g=tuple(tuple(1 for x in range(GRID_SIZE)) for y in range(GRID_SIZE))
        self.assertEqual(oracle_relaxation(g),2*(GRID_SIZE-1))
    def test_oracle_blocked_endpoint(self):
        g=[list(r) for r in create_case(FAMILIES[0],61000)]
        g[0][0]=None
        with self.assertRaises(ValueError):oracle_relaxation(g)
    def test_baseline_matches_separate_oracle(self):
        for f in FAMILIES:
            for seed in SEEDS[:8]:
                grid=create_case(f,seed)
                self.assertEqual(
                    bounded_search(grid,fixed_specs()[0])["cost"],oracle_relaxation(grid))
    def test_admissible_candidate_matches_oracle(self):
        for f in FAMILIES:
            for seed in SEEDS[:8]:
                grid=create_case(f,seed)
                self.assertEqual(
                    bounded_search(grid,fixed_specs()[1])["cost"],oracle_relaxation(grid))
    def test_frozen_proposals(self):
        self.assertEqual(fixed_specs()[2]["weight"],1.25)
    def test_report_no_promotion(self):
        report=evaluate()
        self.assertFalse(report["research_promotion_approved"])
        self.assertFalse(report["production_changes"])
        self.assertEqual(report["evaluation_cases"],256)
        self.assertEqual(report["candidate_evaluations"],768)
    def test_deterministic_report(self):
        self.assertEqual(evaluate(),evaluate())
if __name__=="__main__":unittest.main()
