import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from milestone14_holdout_gate import FROZEN,inspect_holdout,evaluate,run

LABELS=("design_experiment","evaluate_evidence","review_hypothesis","out_of_scope")
def fixtures():
    # Synthetic fixtures check code paths; they are NOT independent labeled data.
    rows=[]
    for label in LABELS:
        for i in range(10):
            rows.append({"label":label,"text":f"synthetic independent fixture {label} tokenxy{chr(97+i)} scenario"})
    data="".join(json.dumps(row)+"\n" for row in rows).encode()
    manifest={"sha256":hashlib.sha256(data).hexdigest(),
        "source_url":"https://example.org/synthetic-fixtures",
        "license":"synthetic-test-only",
        "dataset_id":"test-fixture",
        "collection_method":"unit test constructor",
        "annotation_guidelines_url":"https://example.org/guidelines",
        "reviewer_1":"fixture-A","reviewer_2":"fixture-B",
        "review_utc":"2026-11-19T00:00:00Z",
        "training_data_excluded":True,"validation_data_excluded":True}
    return data,manifest

class HoldoutTests(unittest.TestCase):
    def test_frozen_thresholds(self):
        self.assertEqual(FROZEN,{"word":0.15,"char":0.50})
    def test_valid_fixture(self):
        data,m=fixtures()
        self.assertEqual(len(inspect_holdout(data,m)),40)
    def test_checksum_tamper(self):
        data,m=fixtures()
        with self.assertRaises(ValueError):inspect_holdout(data+b" ",m)
    def test_distinct_reviewers(self):
        data,m=fixtures();m["reviewer_2"]=m["reviewer_1"]
        with self.assertRaises(ValueError):inspect_holdout(data,m)
    def test_review_not_attested(self):
        data,m=fixtures();m["training_data_excluded"]=False
        with self.assertRaises(ValueError):inspect_holdout(data,m)
    def test_missing_review(self):
        data,m=fixtures();del m["review_utc"]
        with self.assertRaises(ValueError):inspect_holdout(data,m)
    def test_leakage(self):
        data,m=fixtures()
        rows=[json.loads(x) for x in data.decode().splitlines()]
        rows[0]["text"]="define baseline dataset split and experiment budget"
        data="".join(json.dumps(x)+"\n" for x in rows).encode()
        m["sha256"]=hashlib.sha256(data).hexdigest()
        with self.assertRaises(ValueError):inspect_holdout(data,m)
    def test_duplicate(self):
        data,m=fixtures()
        rows=[json.loads(x) for x in data.decode().splitlines()]
        rows[1]=rows[0]
        data="".join(json.dumps(x)+"\n" for x in rows).encode()
        m["sha256"]=hashlib.sha256(data).hexdigest()
        with self.assertRaises(ValueError):inspect_holdout(data,m)
    def test_missing_class(self):
        data,m=fixtures()
        rows=[json.loads(x) for x in data.decode().splitlines()]
        rows=[x for x in rows if x["label"]!="out_of_scope"]
        data="".join(json.dumps(x)+"\n" for x in rows).encode()
        m["sha256"]=hashlib.sha256(data).hexdigest()
        with self.assertRaises(ValueError):inspect_holdout(data,m)
    def test_metrics_stay_unpromoted(self):
        data,m=fixtures()
        r=evaluate(inspect_holdout(data,m))
        self.assertFalse(r["promotion_approved"])
        self.assertFalse(r["human_provenance_independently_verified"])
        self.assertFalse(r["production_changes"])
        self.assertEqual(set(r["results"]),{"word","char"})
        self.assertEqual(r["results"]["word"]["ood_total"],10)
    def test_reproducible(self):
        data,m=fixtures()
        rows=inspect_holdout(data,m)
        self.assertEqual(evaluate(rows),evaluate(rows))
    def test_file_command(self):
        data,m=fixtures()
        with tempfile.TemporaryDirectory() as d:
            data_path=Path(d)/"data.jsonl"
            manifest_path=Path(d)/"manifest.json"
            data_path.write_bytes(data)
            manifest_path.write_text(json.dumps(m))
            r=run(data_path,manifest_path)
            self.assertEqual(r["holdout_row_count"],40)
            self.assertFalse(r["promotion_approved"])
    def test_symlink_refused(self):
        data,m=fixtures()
        with tempfile.TemporaryDirectory() as d:
            data_path=Path(d)/"data.jsonl"
            data_path.write_bytes(data)
            manifest_path=Path(d)/"manifest.json"
            manifest_path.write_text(json.dumps(m))
            link=Path(d)/"link"
            link.symlink_to(data_path)
            with self.assertRaises(ValueError):run(link,manifest_path)

if __name__=="__main__":unittest.main()
