import json
from pathlib import Path
import sys,tempfile,unittest
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from health_connect_daily_publish import publish,TAG

class PublishTests(unittest.TestCase):
    def sample(self):
        now=datetime(2026,10,16,22,0,tzinfo=timezone.utc)
        q={"status":"SAFE_SOURCE_ONLY","safe":True,"latest_end_ms":int(now.timestamp()*1000)-60000,
           "local_date":"2026-10-16","total":123,"records":7,"source_package":"com.fitbit.FitbitMobile"}
        return now,{"quality":q}

    def test_idempotent_update_preserves_other_records(self):
        now,c=self.sample()
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"daily_metrics.jsonl"
            target.write_text(json.dumps({"source":"unrelated","steps":30,"timestamp":"2026-10-15T00:00:00+00:00"})+"\n")
            publish(c,target,now)
            c["quality"]["total"]=135
            publish(c,target,now)
            lines=[json.loads(l) for l in target.read_text().splitlines()]
            self.assertEqual(len(lines),2)
            self.assertEqual(lines[-1]["steps"],135)
            self.assertEqual(lines[-1]["source"],TAG)

    def test_stale_rejected_without_overwriting(self):
        now,c=self.sample()
        c["quality"]["latest_end_ms"]-=3*86400*1000
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"daily_metrics.jsonl"
            target.write_text("existing\n")
            with self.assertRaises(ValueError):publish(c,target,now)
            self.assertEqual(target.read_text(),"existing\n")

    def test_unsafe_rejected(self):
        now,c=self.sample()
        c["quality"]["safe"]=False
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"daily_metrics.jsonl"
            with self.assertRaises(ValueError):publish(c,target,now)
            self.assertFalse(target.exists())

if __name__=="__main__":unittest.main()
