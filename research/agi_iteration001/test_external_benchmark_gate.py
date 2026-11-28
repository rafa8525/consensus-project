import hashlib,json,tempfile,unittest
from pathlib import Path
from external_benchmark_gate import (STRESS,benchmark,classification_metrics,
  validate_external,run_external,DEVELOPMENT)
from local_inference import LABELS

def fixture():
    # Construct synthetic fixtures for validation tests, NOT independent provenance.
    words=("alpha","bravo","charlie","delta","echo","foxtrot","golf","hotel","india","juliet")
    rows=[{"label":label,"text":f"unseen synthetic source record {words[i]} for {label}"}
          for label in LABELS for i in range(10)]
    raw=("".join(json.dumps(r)+"\n" for r in rows)).encode()
    manifest={"sha256":hashlib.sha256(raw).hexdigest(),
      "source_url":"https://example.org/fixture","license":"test-only",
      "dataset_id":"synthetic-fixture","annotator_id":"test-harness",
      "collection_method":"constructed in test","heldout_for":"research-task-classification-v1"}
    return raw,manifest

class ExternalGateTests(unittest.TestCase):
    def test_stress_class_balance(self):
        self.assertEqual(len(STRESS),12)
        for label in LABELS:self.assertEqual(sum(y==label for y,_ in STRESS),4)
    def test_metrics_all_correct(self):
        m=classification_metrics(STRESS,[y for y,_ in STRESS])
        self.assertEqual(m["macro_f1"],1.0)
        self.assertEqual(m["correct"],12)
    def test_stress_no_promotion(self):
        r=benchmark()
        self.assertFalse(r["promotion_approved"])
        self.assertEqual(r["evaluation_kind"],"internal_hand_authored_stress")
    def test_valid_fixture_accepted_not_verified(self):
        raw,manifest=fixture()
        self.assertEqual(len(validate_external(raw,manifest)),30)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"data.jsonl";m=Path(d)/"manifest.json"
            p.write_bytes(raw);m.write_text(json.dumps(manifest))
            out=run_external(p,m)
            self.assertFalse(out["independent_provenance_verified"])
            self.assertFalse(out["promotion_approved"])
    def test_hash_mismatch(self):
        raw,manifest=fixture();manifest["sha256"]="0"*64
        with self.assertRaises(ValueError): validate_external(raw,manifest)
    def test_missing_provenance(self):
        raw,manifest=fixture();del manifest["annotator_id"]
        with self.assertRaises(ValueError): validate_external(raw,manifest)
    def test_leakage(self):
        raw,manifest=fixture()
        rows=[json.loads(x) for x in raw.decode().splitlines()]
        rows[0]["text"]=DEVELOPMENT[0][1]
        tampered=("".join(json.dumps(r)+"\n" for r in rows)).encode()
        manifest["sha256"]=hashlib.sha256(tampered).hexdigest()
        with self.assertRaises(ValueError):validate_external(tampered,manifest)
    def test_duplicates(self):
        raw,manifest=fixture()
        rows=[json.loads(x) for x in raw.decode().splitlines()]
        rows[1]=rows[0]
        tampered=("".join(json.dumps(r)+"\n" for r in rows)).encode()
        manifest["sha256"]=hashlib.sha256(tampered).hexdigest()
        with self.assertRaises(ValueError):validate_external(tampered,manifest)
    def test_class_imbalance(self):
        raw,manifest=fixture()
        rows=[json.loads(x) for x in raw.decode().splitlines()]
        rows[10:15]=[{"label":"design_experiment","text":f"switched record text {word}"} for word in ("alpha","bravo","charlie","delta","echo")]
        tampered=("".join(json.dumps(r)+"\n" for r in rows)).encode()
        manifest["sha256"]=hashlib.sha256(tampered).hexdigest()
        with self.assertRaises(ValueError):validate_external(tampered,manifest)
    def test_oversized(self):
        raw,manifest=fixture()
        with self.assertRaises(ValueError):validate_external(raw+b" "*1048577,manifest)
    def test_disallowed_scheme(self):
        raw,manifest=fixture();manifest["source_url"]="http://example.org"
        with self.assertRaises(ValueError):validate_external(raw,manifest)
    def test_bad_label(self):
        raw,manifest=fixture()
        rows=[json.loads(x) for x in raw.decode().splitlines()]
        rows[0]["label"]="production_execute"
        tampered=("".join(json.dumps(r)+"\n" for r in rows)).encode()
        manifest["sha256"]=hashlib.sha256(tampered).hexdigest()
        with self.assertRaises(ValueError):validate_external(tampered,manifest)

if __name__=="__main__":unittest.main()
