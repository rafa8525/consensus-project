"""Synthetic end-to-end candidate tests without private medical data."""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "tools"))
from health_connect_steps_candidate import extract_today, UnsafeRecords

class StepCandidateTests(unittest.TestCase):
    def make_zip(self, root, overlapped=False):
        dbp=Path(root)/"synthetic.db"
        with sqlite3.connect(dbp) as db:
            db.execute("CREATE TABLE steps_record_table(row_id INTEGER,uuid TEXT,app_info_id INTEGER,device_info_id INTEGER,start_time INTEGER,end_time INTEGER,count INTEGER)")
            db.execute("CREATE TABLE application_info_table(row_id INTEGER,package_name TEXT,app_name TEXT)")
            db.execute("CREATE TABLE device_info_table(row_id INTEGER,manufacturer TEXT,model TEXT)")
            db.execute("INSERT INTO application_info_table VALUES(1,'com.fitbit.FitbitMobile','Fitbit')")
            now=datetime.now(timezone.utc)
            begin=now.replace(hour=1,minute=0,second=0,microsecond=0)
            first=int(begin.timestamp()*1000)
            # Testable even when UTC time is before 01:00: choose midnight instead.
            if now < begin.replace(hour=1):
                first=int(now.replace(hour=0,minute=0,second=0,microsecond=0).timestamp()*1000)
            end=min(first+60000,int(now.timestamp()*1000)-1)
            if end <= first:
                end=first+1
            db.execute("INSERT INTO steps_record_table VALUES(1,'one',1,1,?,?,12)",(first,end))
            if overlapped:
                db.execute("INSERT INTO steps_record_table VALUES(2,'two',1,1,?,?,9)",(first,end))
        archive=Path(root)/"Health Connect.zip"
        with zipfile.ZipFile(archive,"w") as z:z.write(dbp,"health_connect_export.db")
        return archive

    def test_candidate_not_production_authorized(self):
        with tempfile.TemporaryDirectory() as t:
            a=self.make_zip(t)
            record=extract_today(a)
            self.assertEqual(record["steps"],12)
            self.assertFalse(record["production_ingest_allowed"])
            self.assertFalse(record["device_verified"])

    def test_overlap_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            a=self.make_zip(t,True)
            with self.assertRaises(UnsafeRecords):
                extract_today(a)

if __name__ == "__main__":
    unittest.main()
