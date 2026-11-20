import unittest
from local_inference import TRAIN, LABELS
from model_improvement_experiment import VALIDATION, TEST
from replicated_model_evaluation import (CONFIRMATION,SEEDS,FOLDS,split_indices,
   paired_bootstrap_interval,macro_f1,run)

class ReplicationTests(unittest.TestCase):
    def test_confirmation_balanced(self):
        self.assertEqual(len(CONFIRMATION),18)
        for label in LABELS:
            self.assertEqual(sum(y==label for y,_ in CONFIRMATION),6)
    def test_split_no_exact_leakage(self):
        texts=[{text.lower() for _,text in x} for x in (TRAIN+VALIDATION,TEST,CONFIRMATION)]
        self.assertFalse(texts[0]&texts[1] or texts[0]&texts[2] or texts[1]&texts[2])
    def test_fold_coverage_and_class_balance(self):
        data=TRAIN+VALIDATION
        for seed in SEEDS:
            folds=split_indices(data,seed)
            self.assertEqual(len(folds),FOLDS)
            self.assertEqual(sorted(i for fold in folds for i in fold),list(range(len(data))))
            for fold in folds:
                self.assertEqual(len(fold),6)
                for label in LABELS:
                    self.assertEqual(sum(data[i][0]==label for i in fold),2)
    def test_reproducible_splits(self):
        self.assertEqual(split_indices(TRAIN+VALIDATION,19),split_indices(TRAIN+VALIDATION,19))
    def test_invalid_small_split(self):
        with self.assertRaises(ValueError):split_indices([TRAIN[0]],7)
    def test_perfect_f1(self):
        actual=list(LABELS)
        self.assertAlmostEqual(macro_f1(actual,actual),1)
    def test_paired_bootstrap_no_difference(self):
        self.assertEqual(paired_bootstrap_interval([1,0,1],[1,0,1]),[0.0,0.0])
    def test_model_is_not_auto_promoted(self):
        r=run()
        self.assertFalse(r["promotion_approved"])
        self.assertFalse(r["production_changes"])
        self.assertEqual(r["number_of_folds"],25)
    def test_results_reproducible(self):
        self.assertEqual(run(),run())
if __name__=="__main__":unittest.main()
