import json,sys,tempfile,unittest
from pathlib import Path
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from health_connect_freshness import verify,TAG
class FreshnessTests(unittest.TestCase):
    def test_valid_and_old(self):
        now=datetime(2026,10,16,22,tzinfo=timezone.utc)
        day=now.astimezone(ZoneInfo("America/Los_Angeles")).date().isoformat()
        obj={"source":TAG,"date_local":day,"timestamp":now.isoformat(),
             "measurement_end_utc":(now-timedelta(minutes=5)).isoformat(),
             "timezone":"America/Los_Angeles","coverage":"partial_day_fitbit_only",
             "steps":3890,"source_records":92}
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"fitness.jsonl"
            p.write_text(json.dumps(obj)+"\n")
            self.assertEqual(verify(p,now)[0],True)
            obj["measurement_end_utc"]=(now-timedelta(days=3)).isoformat()
            p.write_text(json.dumps(obj)+"\n")
            self.assertEqual(verify(p,now)[1],"MEASUREMENTS_STALE")
            p.write_text(json.dumps(obj)+"\n"+json.dumps(obj)+"\n")
            self.assertEqual(verify(p,now)[0],False)
    def test_missing(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertFalse(verify(Path(t)/"missing")[0])
if __name__=="__main__":unittest.main()
