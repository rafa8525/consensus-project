#!/usr/bin/env python3
"""Cloud-side, read-only Health Connect export inspection.

Run on PythonAnywhere after a PRIVATE ZIP has been placed in its private
runtime directory. This is a fail-closed preflight, NOT an ingestion scheduler.
It never publishes medical data or declares ACS-03 healthy.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import zipfile

EXPECTED_ENTRY = "health_connect_export.db"
REQUIRED = {
    "steps_record_table": {"row_id", "uuid", "app_info_id", "device_info_id", "start_time", "end_time", "count"},
    "application_info_table": {"row_id", "package_name", "app_name"},
    "device_info_table": {"row_id", "manufacturer", "model"},
}
MAX_UNCOMPRESSED = 1024 * 1024 * 1024

class ExportError(Exception):
    pass

def inspect_export(archive: Path) -> dict:
    if not archive.is_file() or archive.is_symlink():
        raise ExportError("Archive missing or unsafe path")
    with zipfile.ZipFile(archive) as z:
        entries = z.infolist()
        if len(entries) != 1 or entries[0].filename != EXPECTED_ENTRY:
            raise ExportError("Unexpected export archive structure")
        entry = entries[0]
        if entry.file_size > MAX_UNCOMPRESSED or entry.file_size == 0:
            raise ExportError("Export database size outside allowed bounds")
        with tempfile.TemporaryDirectory(prefix="acs-health-", dir=os.environ.get("ACS_PRIVATE_TMP")) as temp:
            destination = Path(temp) / EXPECTED_ENTRY
            with z.open(entry) as src, destination.open("xb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
            if destination.stat().st_size != entry.file_size:
                raise ExportError("Incomplete database extraction")
            if destination.open("rb").read(16) != b"SQLite format 3\x00":
                raise ExportError("Export is not SQLite")
            uri = destination.as_uri() + "?mode=ro&immutable=1"
            with closing(sqlite3.connect(uri, uri=True)) as db:
                db.execute("PRAGMA query_only=ON")
                tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                for table, required_columns in REQUIRED.items():
                    if table not in tables:
                        raise ExportError("Required table missing: " + table)
                    actual = {r[1] for r in db.execute('PRAGMA table_info("' + table + '")')}
                    if not required_columns.issubset(actual):
                        raise ExportError("Unexpected schema for " + table)
                counts = dict(db.execute(
                    "SELECT COALESCE(a.app_name,a.package_name,'unknown'), COUNT(*) "
                    "FROM steps_record_table AS s "
                    "LEFT JOIN application_info_table AS a ON a.row_id=s.app_info_id "
                    "GROUP BY s.app_info_id"
                ).fetchall())
                if not counts or sum(counts.values()) == 0:
                    raise ExportError("No source step records")
                integrity = db.execute("PRAGMA quick_check").fetchone()[0]
                if integrity != "ok":
                    raise ExportError("Database integrity check failed")
                return {"status": "schema_verified", "step_source_record_counts": counts,
                        "step_records": sum(counts.values()), "can_ingest": False,
                        "reason": "Timestamp units, source priority, overlap policy and cloud delivery remain unvalidated"}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Private cloud-side Health Connect.zip")
    args = parser.parse_args()
    try:
        result = inspect_export(args.archive)
    except (ExportError, OSError, sqlite3.DatabaseError, zipfile.BadZipFile, RuntimeError) as exc:
        print("ACS03_EXPORT_PREFLIGHT=FAIL " + type(exc).__name__, file=sys.stderr)
        return 2
    print("ACS03_EXPORT_PREFLIGHT=PASS")
    print("STEP_RECORDS=" + str(result["step_records"]))
    print("INGESTION_ENABLED=NO")
    print("REASON=" + result["reason"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
