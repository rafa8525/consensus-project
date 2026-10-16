import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from health_connect_step_quality import assess

class Tests(unittest.TestCase):
    def test_clean_records(self):
        q=assess([("a",100,200,12),("b",200,300,9)],0,400)
        self.assertEqual(q["total"],21)
        self.assertTrue(q["safe"])
    def test_overlapping_rejected(self):
        q=assess([("a",100,200,12),("b",199,300,9)],0,400)
        self.assertFalse(q["safe"])
        self.assertIsNone(q["total"])
    def test_duplicate_rejected(self):
        q=assess([("a",100,200,12),("a",200,300,9)],0,400)
        self.assertFalse(q["safe"])
    def test_missing_rejected(self):
        self.assertFalse(assess([],0,400)["safe"])

if __name__=="__main__": unittest.main()
