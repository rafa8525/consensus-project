import sqlite3
import tempfile
import unittest
from pathlib import Path
from three_role_research_cycle import (ROLES,connect,step,snapshot,
  plan,engineer,independent_review,digest,_get)

class ThreeRoleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"queue.db"
        self.con=connect(self.path)
        self.addCleanup(self.con.close)
    def test_initial_pending(self):
        self.assertFalse(snapshot(self.con)["fully_completed"])
    def test_order_enforced(self):
        with self.assertRaises(ValueError):step(self.con,ROLES[1])
        with self.assertRaises(ValueError):step(self.con,ROLES[2])
    def test_end_to_end_three_receipts(self):
        results=[step(self.con,role) for role in ROLES]
        self.assertEqual(len(results),3)
        self.assertTrue(snapshot(self.con)["fully_completed"])
        self.assertTrue(results[2]["output"]["recomputed_validation_matches"])
        self.assertFalse(results[2]["output"]["research_candidate_approved"])
    def test_role_idempotence(self):
        a=step(self.con,ROLES[0]);b=step(self.con,ROLES[0])
        self.assertEqual(a,b)
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM task_receipts").fetchone()[0],1)
    def test_receipt_tamper_rejected(self):
        step(self.con,ROLES[0])
        self.con.execute("UPDATE task_receipts SET output_json='{}' WHERE role=?",(ROLES[0],))
        with self.assertRaises(ValueError):step(self.con,ROLES[1])
    def test_plan_bounded(self):
        p=plan()
        self.assertEqual(len(p["alternatives"]),3)
        self.assertEqual(p["budget"]["max_model_fits"],3)
    def test_engineer_does_not_evaluate_test(self):
        a=step(self.con,ROLES[0])
        b=engineer(a)
        self.assertFalse(b["test_evaluated"])
        self.assertTrue(b["selection_uses_validation_only"])
    def test_independent_evaluator_recomputes(self):
        a=step(self.con,ROLES[0])
        b=step(self.con,ROLES[1])
        altered=dict(b)
        altered["output"]=dict(b["output"])
        altered["output"]["outcomes"]=[]
        with self.assertRaises(ValueError):independent_review(a,altered)
    def test_unauthorized_role_refused(self):
        with self.assertRaises(ValueError):step(self.con,"external_operator")
    def test_persistence_reopen(self):
        for role in ROLES:step(self.con,role)
        self.con.close()
        c=connect(self.path)
        try:self.assertTrue(snapshot(c)["fully_completed"])
        finally:c.close()
    def test_reproducible_result(self):
        for role in ROLES:step(self.con,role)
        first=snapshot(self.con)
        for role in ROLES:step(self.con,role)
        self.assertEqual(first,snapshot(self.con))
if __name__=="__main__":unittest.main()
