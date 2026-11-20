import unittest
from datetime import datetime,timezone,timedelta
from acs_public_triage import assess

NOW=datetime(2026,11,20,4,0,tzinfo=timezone.utc)
def sample(age=1):
    return {"generated_at_utc":(NOW-timedelta(hours=age)).isoformat(),
      "agents":{f"ACS-{i:02}":{"status":"current","health_status":"healthy"} for i in range(1,6)}}

class TriageTests(unittest.TestCase):
    def test_healthy(self):
        x=assess(sample(),NOW);self.assertEqual(len(x["healthy_agents"]),5)
        self.assertFalse(x["phase1_certified"])
    def test_stale(self):
        self.assertFalse(assess(sample(31),NOW)["fresh_within_30_hours"])
    def test_future_rejected(self):
        self.assertFalse(assess(sample(-1),NOW)["fresh_within_30_hours"])
    def test_acs03_errors(self):
        x=sample()
        x["agents"]["ACS-03"]={"status":"degraded","health_status":"execution_failure",
            "diagnostics":{"components":[{"component":"health_connect_cloud_cycle","status":"execution_failure","returncode":2},
                {"component":"fitness_tracking_verifier","status":"execution_failure","returncode":1}]}}
        got=assess(x,NOW)
        self.assertEqual(len(got["acs03_failed_components"]),2)
        self.assertFalse(got["production_repair_performed"])
    def test_acs05_codes(self):
        x=sample()
        x["agents"]["ACS-05"]={"status":"degraded","health_status":"critical",
             "diagnostics":{"issue_codes":["ORCHESTRATION_WIRING_WARNING","ALERT_DELIVERY_WARNING","private-info"]}}
        self.assertEqual(len(assess(x,NOW)["acs05_issue_codes"]),2)
    def test_missing_agents(self):
        x=sample();del x["agents"]["ACS-03"]
        self.assertTrue(any(z["reason"]=="missing_agent" for z in assess(x,NOW)["unhealthy_findings"]))
    def test_invalid_timestamp(self):
        x=sample();x["generated_at_utc"]="not-a-date"
        with self.assertRaises(ValueError): assess(x,NOW)
if __name__=="__main__":unittest.main()
