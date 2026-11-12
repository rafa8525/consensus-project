import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import health_connect_cloud_cycle as m
class CycleTests(unittest.TestCase):
    def test_success(self):
        with patch.object(m.resource,"getrlimit",return_value=(-1,-1)),patch.object(m.resource,"setrlimit"),patch.object(m,"import_candidate",return_value={"quality":{}}),patch.object(m,"publish",return_value={"local_date":"2026-10-16","records":92}),patch.object(m,"verify",return_value=(True,"VERIFIED_PARTIAL_DAY")):
            self.assertEqual(m.main(),0)
    def test_failure_does_not_claim_success(self):
        with patch.object(m.resource,"getrlimit",return_value=(-1,-1)),patch.object(m.resource,"setrlimit"),patch.object(m,"import_candidate",side_effect=ValueError("stale")):
            self.assertEqual(m.main(),2)
if __name__=="__main__":unittest.main()
