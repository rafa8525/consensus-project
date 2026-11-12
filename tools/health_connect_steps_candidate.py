#!/usr/bin/env python3
"""Cloud-only Health Connect daily steps candidate: source-scoped, fail-closed.

This does not feed production ACS-03 yet. Produces a private candidate JSON
for human/automated validation of real data and timestamp units.
"""
from __future__ import annotations
from contextlib import closing
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import zipfile
import shutil

from health_connect_cloud_preflight import EXPECTED_ENTRY, inspect_export

class UnsafeRecords(Exception):
    pass

PREFERRED_PACKAGES = ("com.fitbit.FitbitMobile",)
MIN_EPOCH_MS = 946684800000
MAX_EPOCH_MS = 4102444800000

def extract_today(archive: Path, now: datetime | None = None) -> dict:
    # Schema and archive integrity must pass before any reads.
    inspect_export(archive)
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise UnsafeRecords("Naive clock value")
    today = now.astimezone(timezone.utc).date()
    start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    floor_ms = int(start.timestamp() * 1000)
    ceiling_ms = min(int(end.timestamp() * 1000), int(now.timestamp() * 1000) + 300000)
    with tempfile.TemporaryDirectory(prefix="acs03-ingest-", dir=os.environ.get("ACS_PRIVATE_TMP")) as temp:
        db_file = Path(temp) / EXPECTED_ENTRY
        with zipfile.ZipFile(archive) as z:
            with z.open(EXPECTED_ENTRY) as src, db_file.open("xb") as dst:
                shutil.copyfileobj(src, dst)
        with closing(sqlite3.connect(db_file.as_uri()+"?mode=ro&immutable=1", uri=True)) as db:
            db.execute("PRAGMA query_only=ON")
            # A record's presence or app name does not prove its physical watch.
            # Select only the exact source package explicitly authorized.
            apps = db.execute(
                "SELECT row_id,package_name FROM application_info_table WHERE package_name = ?",
                (PREFERRED_PACKAGES[0],)
            ).fetchall()
            if len(apps) != 1:
                raise UnsafeRecords("Expected Fitbit source package not confirmed")
            app_id = apps[0][0]
            # Reject unknown epoch units instead of assuming timestamps are ms.
            sample = db.execute(
                "SELECT start_time,end_time FROM steps_record_table WHERE app_info_id=? "
                "ORDER BY start_time DESC LIMIT 1", (app_id,)
            ).fetchone()
            if not sample or any(not isinstance(x, int) or not MIN_EPOCH_MS <= x < MAX_EPOCH_MS for x in sample):
                raise UnsafeRecords("Unverified timestamp units")
            rows = db.execute(
                "SELECT uuid,start_time,end_time,count FROM steps_record_table "
                "WHERE app_info_id=? AND start_time>=? AND end_time<=? "
                "ORDER BY start_time,end_time,uuid", (app_id, floor_ms, ceiling_ms)
            ).fetchall()
    if not rows:
        raise UnsafeRecords("No preferred-source records for current UTC day")
    total = 0
    last_end = None
    seen = set()
    for uuid, first, last, count in rows:
        if not isinstance(uuid,str) or not uuid or uuid in seen:
            raise UnsafeRecords("Missing or duplicate record identifier")
        seen.add(uuid)
        if not all(isinstance(x,int) and not isinstance(x,bool) for x in (first,last,count)):
            raise UnsafeRecords("Invalid time or count field")
        if first >= last or first < floor_ms or last > ceiling_ms or count < 0:
            raise UnsafeRecords("Invalid or out-of-day step record")
        if last_end is not None and first < last_end:
            raise UnsafeRecords("Overlapping Fitbit source records; cannot sum safely")
        if count > 100000:
            raise UnsafeRecords("Implausible interval step count")
        total += count
        last_end = last
    return {
        "timestamp": now.astimezone(timezone.utc).isoformat(),
        "date_utc": today.isoformat(),
        "steps": total,
        "source": "health_connect_export",
        "source_app_package": PREFERRED_PACKAGES[0],
        "source_records": len(rows),
        "coverage": "partial_day_source_only",
        "device_verified": False,
        "production_ingest_allowed": False,
    }

def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    p.add_argument("--output", type=Path, default=Path.home() / "acs-runtime/health-connect/steps_candidate.json")
    a = p.parse_args()
    try:
        private_root = Path(os.environ.get("ACS_PRIVATE_RUNTIME", Path.home() / "acs-runtime")).resolve()
        target = a.output.resolve()
        if private_root not in target.parents or a.output.is_symlink():
            raise UnsafeRecords("Output must be inside private runtime")
        result = extract_today(a.archive)
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(target.parent, 0o700)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as handle:
            tmp = Path(handle.name)
            os.chmod(tmp, 0o600)
            json.dump(result, handle, sort_keys=True)
            handle.write("\n")
        try:
            os.replace(tmp, target)
        finally:
            tmp.unlink(missing_ok=True)
    except Exception as exc:
        print("ACS03_CANDIDATE=FAIL "+type(exc).__name__, file=sys.stderr)
        return 2
    print("ACS03_CANDIDATE=READY_FOR_VALIDATION")
    print("PRODUCTION_INGEST=DISABLED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
