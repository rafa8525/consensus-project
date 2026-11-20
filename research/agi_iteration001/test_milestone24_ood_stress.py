import unittest
from milestone24_ood_stress import KINDS,IN_KINDS,OOD_KINDS,SEEDS,task,one,execute

class M24OODTests(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(sum(len(s) for s in SEEDS.values()),60)
        self.assertEqual(sum(len(SEEDS[x]) for x in IN_KINDS),30)
        self.assertEqual(sum(len(SEEDS[x]) for x in OOD_KINDS),30)
    def test_same_case(self):
        self.assertEqual(task("mixed",120000),task("mixed",120000))
    def test_reject_unknown(self):
        with self.assertRaises(ValueError):task("injected",123)
    def test_no_demo_query_overlap(self):
        for kind in KINDS:
            a,b=task(kind,SEEDS[kind][0])
            self.assertFalse({(x,z) for x,z,_ in a}&{(x,z) for x,z,_ in b})
    def test_rule_results_scoped(self):
        r=one("affine",110000)
        self.assertTrue(r["in_language"])
        self.assertEqual(r["queries"],16)
    def test_ood_label(self):
        r=one("mixed",120000)
        self.assertFalse(r["in_language"])
    def test_reproducible(self):
        self.assertEqual(execute(),execute())
    def test_no_promotion(self):
        result=execute()
        self.assertFalse(result["promotion_approved"])
        self.assertFalse(result["externally_sourced"])
        self.assertEqual(result["live_model_calls"],0)
        self.assertEqual(result["in_domain"]["tasks"],30)
        self.assertEqual(result["out_of_domain"]["tasks"],30)
    def test_total_queries(self):
        result=execute()
        self.assertEqual(result["in_domain"]["total_queries"]+result["out_of_domain"]["total_queries"],960)
if __name__=="__main__":unittest.main()
