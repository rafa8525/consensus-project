"""Strict no-cost regression checks for bounded proposal evaluation."""
import copy
import json
import unittest
from unittest.mock import patch
import bounded_proposal_evaluation as bounded
from proposal_provider import OfflineProposalProvider

class BoundedProposalEvaluationTests(unittest.TestCase):
    def test_exact_three_fits_and_no_holdout(self):
        real_fit_word=bounded.fit_word
        real_train_char=bounded.train_char
        counters={"word":0,"char":0}
        def word(*args,**kwargs):
            counters["word"]+=1
            return real_fit_word(*args,**kwargs)
        def char(*args,**kwargs):
            counters["char"]+=1
            return real_train_char(*args,**kwargs)
        with patch.object(bounded,"fit_word",side_effect=word), patch.object(
                bounded,"train_char",side_effect=char):
            result=bounded.evaluate()
        self.assertEqual(counters,{"word":1,"char":2})
        self.assertEqual(result["fit_count"],3)
        self.assertEqual(result["split_sizes"],{"train":18,"validation":12})
        self.assertFalse(result["holdout_accessed"])
        self.assertFalse(result["promotion_approved"])
        self.assertFalse(result["production_changes"])
        self.assertEqual(result["api_calls"],0)
        self.assertFalse(result["independent_generalization_verified"])
    def test_reproducible_report(self):
        self.assertEqual(bounded.evaluate(),bounded.evaluate())
        result=bounded.evaluate()
        self.assertEqual(len(result["dataset_sha256"]),64)
        self.assertEqual(result["selected_index_by_validation"],
                         sorted(range(3),key=lambda i:(
                             -result["evaluations"][i]["validation_macro_f1"],i))[0])
        for row in result["evaluations"]:
            self.assertLessEqual(row["validation_macro_f1"],1)
            self.assertGreaterEqual(row["validation_macro_f1"],0)
            self.assertEqual(row["validation_total"],12)
    def test_rejects_wrong_catalog_before_any_fits(self):
        proposal=json.loads(OfflineProposalProvider().propose())
        proposal["alternatives"][1]["alpha"]=4.0
        with patch.object(bounded,"fit_word") as wf, patch.object(
                 bounded,"train_char") as cf:
            with self.assertRaises(ValueError):
                bounded.evaluate(proposal)
            wf.assert_not_called()
            cf.assert_not_called()
    def test_rejects_oversized_training_split(self):
        examples=tuple(bounded.TRAIN)*2
        with self.assertRaises(ValueError):
            bounded._check_data(examples,tuple(bounded.VALIDATION))
    def test_detects_train_validation_leakage(self):
        modified=list(bounded.VALIDATION)
        modified[0]=tuple(bounded.TRAIN[0])
        with self.assertRaises(ValueError):
            bounded._check_data(tuple(bounded.TRAIN),tuple(modified))
    def test_reporting_does_not_claim_live_proposal_execution(self):
        result=bounded.evaluate()
        self.assertEqual(result["proposal_origin"],
                         "fixed_offline_fixture_not_recovered_live_output")
        self.assertEqual(result["metric"],"validation_macro_f1")
        self.assertEqual(result["max_model_fits"],3)
    def test_approved_proposal_fixture_equivalence(self):
        fixture=OfflineProposalProvider().propose()
        self.assertEqual(bounded.evaluate(fixture),bounded.evaluate())
if __name__=="__main__":unittest.main()
