import json
import tempfile
import unittest
from pathlib import Path
from solo_vs_team_planning import (CANDIDATES,SEEDS_DEV,SEEDS_TEST,
    make_grid,search,benchmark,select,run)

class PlanningBenchmarkTests(unittest.TestCase):
    def test_disjoint_seeds(self):
        self.assertFalse(set(SEEDS_DEV)&set(SEEDS_TEST))
        self.assertEqual(len(SEEDS_DEV),24)
        self.assertEqual(len(SEEDS_TEST),64)
    def test_reproducible_graphs(self):
        self.assertEqual(make_grid(1000),make_grid(1000))
        self.assertNotEqual(make_grid(1000),make_grid(1001))
    def test_grid_has_path(self):
        for seed in (1000,1001,9000):
            self.assertTrue(search(make_grid(seed),"dijkstra")["solved"])
    def test_dijkstra_beats_or_matches_candidate(self):
        for seed in (1000,1002,9000,9005):
            g=make_grid(seed)
            optimal=search(g,"dijkstra")["cost"]
            self.assertGreaterEqual(search(g,"astar_weighted")["cost"],optimal)
    def test_admissible_astar_optimal(self):
        for seed in (1000,1001,1002,1003,9000,9001):
            g=make_grid(seed)
            self.assertEqual(search(g,"dijkstra")["cost"],
                             search(g,"astar_manhattan")["cost"])
    def test_candidate_allowlist(self):
        with self.assertRaises(ValueError):search(make_grid(1000),"arbitrary_python")
        with self.assertRaises(ValueError):benchmark("bad",[1000])
    def test_selection_ignores_nonoptimal_even_if_fast(self):
        data={x:{"cases":24,"optimal_cases":24,"avg_expansions":40}
              for x in CANDIDATES}
        data["astar_weighted"]={"cases":24,"optimal_cases":23,"avg_expansions":2}
        self.assertNotEqual(select(data),"astar_weighted")
    def test_pipeline_same_holdout(self):
        result=run()
        self.assertTrue(result["same_selection"])
        self.assertTrue(result["same_holdout_metrics"])
        self.assertTrue(result["team"]["recomputed_dev"])
        self.assertFalse(result["promotion_approved"])
    def test_budget_and_overhead(self):
        result=run()
        self.assertEqual(result["common_budget"]["development_candidate_evaluations"],72)
        self.assertEqual(result["team"]["extra_development_verification_evaluations"],72)
        self.assertEqual(result["real_ai_agents"],0)
    def test_no_test_selection(self):
        result=run()
        self.assertEqual(result["solo"]["development"],result["team"]["development"])
        self.assertNotEqual(result["seed_set_digests"]["development"],
                            result["seed_set_digests"]["test"])
    def test_repeated_deterministic(self):
        self.assertEqual(run(),run())
if __name__=="__main__":unittest.main()
