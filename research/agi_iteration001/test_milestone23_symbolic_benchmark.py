import unittest
from milestone23_symbolic_benchmark import (
  FAMILIES,POLICIES,DEV_SEEDS,TEST_SEEDS,MOD,calculate,
  discover,make_task,run_one,collect,choose,execute)

class M23SymbolicBenchmarkTests(unittest.TestCase):
    def test_development_size(self):
        self.assertEqual(sum(map(len,DEV_SEEDS.values())),36)
    def test_evaluation_size(self):
        self.assertEqual(sum(map(len,TEST_SEEDS.values())),60)
    def test_no_overlap(self):
        for fam in FAMILIES:
            self.assertFalse(set(DEV_SEEDS[fam])&set(TEST_SEEDS[fam]))
    def test_program_family_differences(self):
        self.assertNotEqual(calculate("affine",2,3,4,2,4),
                            calculate("square",2,3,4,2,4))
    def test_distinct_demonstrations_and_queries(self):
        for f in FAMILIES:
            d,q=make_task(f,DEV_SEEDS[f][0])
            self.assertEqual(len(d),8)
            self.assertEqual(len(q),16)
            self.assertFalse({(x,z) for x,z,_ in d}&{(x,z) for x,z,_ in q})
    def test_task_reproducibility(self):
        self.assertEqual(make_task("affine",81000),make_task("affine",81000))
    def test_disallowed_task(self):
        with self.assertRaises(ValueError):make_task("affine",40000)
    def test_disallowed_policy(self):
        d,_=make_task("affine",81000)
        with self.assertRaises(ValueError):discover(d,"run_code")
    def test_malformed_demos(self):
        d,_=make_task("affine",81000)
        with self.assertRaises(ValueError):discover(d[:-1],"affine_search")
    def test_true_program_can_be_recovered(self):
        for f in FAMILIES:
            d,q=make_task(f,DEV_SEEDS[f][1])
            ans=run_one("three_family_search",d,q)
            self.assertGreater(sum(u==v[2] for u,v in zip(ans["predictions"],q)),8)
    def test_selection_only_development(self):
        dev=collect(DEV_SEEDS)
        self.assertIn(choose(dev),POLICIES)
    def test_full_report(self):
        r=execute()
        self.assertEqual(r["test"][r["selected"]]["total"],960)
        self.assertFalse(r["selection_uses_test"])
        self.assertFalse(r["promotion_approved"])
    def test_deterministic_results(self):
        self.assertEqual(execute(),execute())

if __name__=="__main__":unittest.main()
