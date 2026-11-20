import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from clinc_ood_protocol import (read_original,evaluate_ood,known_fraction,MIN_KNOWN_FRACTION)

class OODProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"clinc.json"
        # Synthetic OOD test fixtures. Not external CLINC150 and not an accuracy result.
        def word(i):
            chars=[]
            for _ in range(3):
                chars.append(chr(97+i%26))
                i//=26
            return "".join(chars)
        self.rows=[[f"synthetic shopping request {word(i)} about air tickets", "oos"] for i in range(45)]
        self.data={"oos_test":self.rows}
    def saved(self):
        raw=json.dumps(self.data).encode("utf-8")
        self.path.write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()
    def test_load_and_deterministic_order(self):
        sha=self.saved()
        a=read_original(self.path,sha)
        b=read_original(self.path,sha)
        self.assertEqual(a,b)
        self.assertEqual(len(a),45)
    def test_source_tamper_blocked(self):
        sha=self.saved()
        self.path.write_text("{}",encoding="utf8")
        with self.assertRaises(ValueError):read_original(self.path,sha)
    def test_missing_oos_blocked(self):
        self.data={"train":self.rows}
        with self.assertRaises(ValueError):read_original(self.path,self.saved())
    def test_bad_label_blocked(self):
        self.rows[2][1]="not_oos"
        with self.assertRaises(ValueError):read_original(self.path,self.saved())
    def test_duplicate_rejection(self):
        self.rows[1]=self.rows[0][:]
        sha=self.saved()
        self.assertEqual(len(read_original(self.path,sha)),44)
    def test_size_limit_and_symlink(self):
        sha=self.saved()
        link=Path(self.tmp.name)/"link"
        link.symlink_to(self.path)
        with self.assertRaises(ValueError):read_original(link,sha)
        with self.assertRaises(ValueError):read_original(self.path,sha,1001)
    def test_coverage_bounds(self):
        self.assertEqual(known_fraction("abc",{"abc"},"word"),1.0)
        self.assertEqual(known_fraction("abc",set(),"word"),0.0)
        self.assertEqual(MIN_KNOWN_FRACTION,0.25)
    def test_not_promoted(self):
        oos=[row[0] for row in self.rows]
        result=evaluate_ood(oos)
        self.assertFalse(result["promotion_approved"])
        self.assertFalse(result["production_changes"])
        self.assertEqual(result["scope"],"cross_domain_rejection_only")
        for key in ("baseline","candidate"):
            self.assertEqual(result[key]["out_of_scope_total"],45)
            self.assertTrue(0<=result[key]["out_of_scope_false_accept_rate"]<=1)
    def test_reproducible_scores(self):
        oos=[r[0] for r in self.rows]
        self.assertEqual(evaluate_ood(oos),evaluate_ood(oos))

if __name__=="__main__":
    unittest.main()
