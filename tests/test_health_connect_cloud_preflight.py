"""Synthetic regression tests; no real medical data or tokens used."""
import importlib.util
from pathlib import Path
import sqlite3
import tempfile
import unittest
import zipfile

MODULE = Path(__file__).resolve().parents[1] / "tools" / "health_connect_cloud_preflight.py"
spec = importlib.util.spec_from_file_location("acs03_preflight", MODULE)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)

class CloudExportPreflightTest(unittest.TestCase):
    def test_verified_schema_without_ingestion(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            dbfile = root / "test.db"
            with sqlite3.connect(dbfile) as db:
                db.execute("CREATE TABLE steps_record_table(row_id INTEGER, uuid TEXT, app_info_id INTEGER, device_info_id INTEGER, start_time INTEGER, end_time INTEGER, count INTEGER)")
                db.execute("CREATE TABLE application_info_table(row_id INTEGER, package_name TEXT, app_name TEXT)")
                db.execute("CREATE TABLE device_info_table(row_id INTEGER, manufacturer TEXT, model TEXT)")
                db.execute("INSERT INTO application_info_table VALUES(1,'com.example.fitness','Synthetic Fitness')")
                db.execute("INSERT INTO steps_record_table VALUES(1,'fake',1,1,100,200,5)")
            archive = root / "Health Connect.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.write(dbfile, "health_connect_export.db")
            result = preflight.inspect_export(archive)
            self.assertEqual(result["step_records"], 1)
            self.assertFalse(result["can_ingest"])

    def test_rejects_unexpected_zip_contents(self):
        with tempfile.TemporaryDirectory() as t:
            archive = Path(t) / "Health Connect.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("wrong.db", "placeholder")
            with self.assertRaises(preflight.ExportError):
                preflight.inspect_export(archive)

    def test_missing_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(preflight.ExportError):
                preflight.inspect_export(Path(t) / "missing.zip")

if __name__ == "__main__":
    unittest.main()
