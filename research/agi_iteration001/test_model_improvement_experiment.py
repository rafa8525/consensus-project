import unittest
from model_improvement_experiment import TRAIN,VALIDATION,TEST,LABELS,_features,train_char,predict_char,score,run
class ModelImprovementTests(unittest.TestCase):
    def test_splits_disjoint(self):
        groups=[set(t.lower() for _,t in x) for x in (TRAIN,VALIDATION,TEST)]
        self.assertFalse(groups[0]&groups[1])
        self.assertFalse(groups[0]&groups[2])
        self.assertFalse(groups[1]&groups[2])
    def test_balanced_fixed_sets(self):
        for rows,n in ((TRAIN,6),(VALIDATION,4),(TEST,4)):
            for label in LABELS:self.assertEqual(sum(y==label for y,_ in rows),n)
    def test_character_features(self):
        self.assertIn("c:^des",_features("design",4))
        self.assertIn("w:design",_features("design",4))
    def test_training_deterministic(self):
        a=train_char()
        b=train_char()
        self.assertEqual(a,b)
    def test_predictions_valid(self):
        m=train_char()
        for y,t in TEST: self.assertIn(predict_char(m,t),LABELS)
    def test_invalid_parameters(self):
        with self.assertRaises(ValueError): train_char(n=2)
        with self.assertRaises(ValueError): train_char(alpha=0)
    def test_scores_account_for_all(self):
        m=train_char()
        s=score(lambda text:predict_char(m,text),TEST)
        self.assertEqual(s["total"],12)
        self.assertEqual(sum(sum(v.values()) for v in s["confusion"].values()),12)
    def test_internal_candidate_eligibility_is_never_promotion(self):
        r=run()
        b=r["baseline"]; c=r["candidate"]
        expected=(c["validation"]["correct"]>b["validation"]["correct"] and
                  c["test"]["correct"]>=b["test"]["correct"])
        self.assertEqual(r["research_candidate_eligible"],expected)
        self.assertFalse(r["promotion_approved"])
        self.assertEqual(r["promotion_scope"],"not_approved_internal_hand_authored_data")
        self.assertFalse(r["production_changes"])
    def test_reproducible_results(self):
        self.assertEqual(run(),run())
if __name__=="__main__":unittest.main()
