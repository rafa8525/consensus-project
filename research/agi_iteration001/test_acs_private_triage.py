import json
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from acs_private_triage import diagnose, fitness_evidence

NOW = datetime(2026, 11, 20, 4, 0, tzinfo=timezone.utc)
class PrivateTriageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/"memory"/"agents").mkdir(parents=True)
        (self.root/"memory"/"logs"/"fitness").mkdir(parents=True)
        (self.root/"memory"/"logs"/"system").mkdir(parents=True)
    def write(self, relative, value):
        path=self.root/"memory"/relative
        path.write_text(json.dumps(value), encoding="utf-8")
        return path
    def test_missing_state(self):
        d=diagnose(self.root,now=NOW)
        self.assertEqual(d["acs03_state"],"missing_or_unreadable")
        self.assertEqual(d["fitness_input"],"source_missing")
    def test_fitness_valid_recent(self):
        self.write("logs/fitness/daily_metrics.jsonl",{"timestamp":NOW.isoformat(),"steps":120})
        self.assertEqual(diagnose(self.root,now=NOW)["fitness_input"],"current")
    def test_fitness_stale(self):
        self.write("logs/fitness/daily_metrics.jsonl",
                   {"timestamp":(NOW-timedelta(days=3)).isoformat(),"steps":120})
        self.assertEqual(diagnose(self.root,now=NOW)["fitness_input"],"stale_over_24h")
    def test_fitness_no_valid_data(self):
        self.write("logs/fitness/daily_metrics.jsonl",{"timestamp":NOW.isoformat(),"steps":"not-a-number"})
        self.assertEqual(diagnose(self.root,now=NOW)["fitness_input"],"no_valid_measurements")
    def test_symlink_refused(self):
        source=self.root/"memory"/"logs"/"fitness"/"daily_metrics.jsonl"
        target=self.root/"outside.json"
        target.write_text("{}")
        source.symlink_to(target)
        self.assertEqual(fitness_evidence(source,NOW),"symlink_rejected")
    def test_acs03_sanitized(self):
        self.write("agents/acs03_state.json",{
            "status":"execution_failure",
            "results":[{"component":"health_connect_cloud_cycle","status":"execution_failure",
                         "returncode":2,"stderr":"TOP_SECRET","error":"secret-token"}]})
        d=diagnose(self.root,now=NOW)
        self.assertEqual(d["acs03_components"][0]["returncode"],2)
        self.assertNotIn("TOP_SECRET",json.dumps(d))
        self.assertNotIn("secret-token",json.dumps(d))
    def test_acs05_sanitized(self):
        self.write("agents/acs05_state.json",{"status":"critical","results":[]})
        self.write("logs/system/continuity_guardian_state.json",
                   {"critical":["private email and token"],"warnings":["private phone"]})
        d=diagnose(self.root,now=NOW)
        self.assertEqual(d["guardian_summary"][0]["count"],1)
        self.assertNotIn("private email",json.dumps(d))
        self.assertNotIn("private phone",json.dumps(d))
    def test_malformed_state_rejected(self):
        (self.root/"memory"/"agents"/"acs05_state.json").write_text("not json")
        self.assertEqual(diagnose(self.root,now=NOW)["acs05_state"],"missing_or_unreadable")

if __name__=="__main__":unittest.main()
