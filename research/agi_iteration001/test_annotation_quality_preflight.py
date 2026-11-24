"""Synthetic vote-metadata tests only; no dataset texts or real annotators."""
import unittest
from annotation_quality_preflight import annotation_quality
from local_inference import LABELS

def synthetic(n=60,disagree=0):
    rows=[]
    for i in range(n):
        y=LABELS[i%3]
        other=LABELS[(i+1)%3] if i<disagree else y
        rows.append({"item_id":f"synthetic-{i}",
                     "annotator_a":"synthetic-rater-a",
                     "annotator_b":"synthetic-rater-b",
                     "vote_a":y,"vote_b":other,
                     "adjudicator":"synthetic-independent-reviewer",
                     "adjudicated_label":y})
    return rows

class AnnotationPreflightTests(unittest.TestCase):
    def test_high_agreement_is_not_provenance(self):
        r=annotation_quality(synthetic())
        self.assertTrue(r["annotation_metadata_quality_passed"])
        self.assertEqual(r["record_count"],60)
        self.assertEqual(r["adjudicated_class_counts"],dict.fromkeys(LABELS,20))
        self.assertEqual(r["cohens_kappa"],1.0)
        for key in ("actual_human_independence_verified","consent_or_rights_verified",
                    "near_duplicate_review_verified","independent_provenance_verified",
                    "external_validation_authorized","promotion_approved","data_imported"):
            self.assertFalse(r[key])
    def test_disagreements_lower_agreement_and_kappa(self):
        r=annotation_quality(synthetic(disagree=30))
        self.assertEqual(r["disagreement_count"],30)
        self.assertAlmostEqual(r["raw_agreement"],0.5)
        self.assertFalse(r["annotation_metadata_quality_passed"])
    def test_insufficient_samples_block(self):
        r=annotation_quality(synthetic(30))
        self.assertFalse(r["count_gate_passed"])
    def test_identical_marginals_degenerate_kappa(self):
        rows=synthetic()
        for row in rows:
            row["vote_a"]=LABELS[0]
            row["vote_b"]=LABELS[0]
            row["adjudicated_label"]=LABELS[0]
        r=annotation_quality(rows)
        self.assertIsNone(r["cohens_kappa"])
        self.assertFalse(r["annotation_metadata_quality_passed"])
    def test_duplicate_ids_rejected(self):
        rows=synthetic()
        rows[1]["item_id"]=rows[0]["item_id"]
        with self.assertRaises(ValueError):annotation_quality(rows)
    def test_annotator_self_review_rejected(self):
        rows=synthetic()
        rows[0]["adjudicator"]=rows[0]["annotator_a"]
        with self.assertRaises(ValueError):annotation_quality(rows)
    def test_unknown_label_rejected(self):
        rows=synthetic()
        rows[0]["vote_b"]="unsafe-label"
        with self.assertRaises(ValueError):annotation_quality(rows)
    def test_unexpected_raw_text_field_rejected(self):
        rows=synthetic()
        rows[0]["text"]="Not allowed in metadata evaluator"
        with self.assertRaises(ValueError):annotation_quality(rows)
    def test_unexplained_override_rejected(self):
        rows=synthetic()
        rows[0]["adjudicated_label"]=LABELS[1]
        with self.assertRaises(ValueError):annotation_quality(rows)
    def test_empty_records_fail_closed(self):
        r=annotation_quality([])
        self.assertIsNone(r["cohens_kappa"])
        self.assertFalse(r["annotation_metadata_quality_passed"])
    def test_bad_id_rejected(self):
        rows=synthetic()
        rows[0]["item_id"]="file:../../private"
        with self.assertRaises(ValueError):annotation_quality(rows)

if __name__=="__main__":unittest.main()
