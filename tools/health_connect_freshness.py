#!/usr/bin/env python3
"""Fail-closed ACS-03 verified source freshness; no log-mtime shortcuts."""
from datetime import datetime,timezone,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import json,sys

PATH=Path("/home/rafa1215/consensus-project/memory/logs/fitness/daily_metrics.jsonl")
TAG="health_connect_fitbit_snapshot_v1"
def verify(path=PATH,now=None):
    now=now or datetime.now(timezone.utc)
    today=now.astimezone(ZoneInfo("America/Los_Angeles")).date().isoformat()
    if path.is_symlink() or not path.is_file():
        return False,"MISSING_RECORD_FILE"
    try:
        values=[json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        records=[r for r in values if isinstance(r,dict) and r.get("source")==TAG and r.get("date_local")==today]
        if len(records)!=1:return False,"MISSING_OR_DUPLICATE_DAILY_RECORD"
        row=records[0]
        steps=row.get("steps")
        if type(steps) is not int or not 0<=steps<=100000:return False,"INVALID_STEPS"
        if row.get("timezone")!="America/Los_Angeles" or row.get("coverage")!="partial_day_fitbit_only":
            return False,"UNEXPECTED_PROVENANCE"
        if type(row.get("source_records")) is not int or row["source_records"]<=0:
            return False,"MISSING_SOURCE_RECORDS"
        end=datetime.fromisoformat(row["measurement_end_utc"].replace("Z","+00:00"))
        imported=datetime.fromisoformat(row["timestamp"].replace("Z","+00:00"))
        if end.tzinfo is None or imported.tzinfo is None:return False,"NAIVE_TIMESTAMPS"
        age=(now-end).total_seconds()
        write_age=(now-imported).total_seconds()
        if not -300<=age<=48*3600:return False,"MEASUREMENTS_STALE"
        if not -300<=write_age<=24*3600:return False,"IMPORT_STALE"
        if end>imported+timedelta(minutes=5):return False,"MEASUREMENT_AFTER_IMPORT"
        return True,"VERIFIED_PARTIAL_DAY"
    except (ValueError,TypeError,KeyError,OSError,json.JSONDecodeError):
        return False,"MALFORMED_RECORDS"

def main():
    ok,reason=verify()
    print("ACS03_SOURCE_FRESHNESS="+("PASS" if ok else "FAIL"))
    print("ACS03_SOURCE_STATUS="+reason)
    print("FULL_DAY_COVERAGE_VERIFIED=NO")
    return 0 if ok else 2
if __name__=="__main__":raise SystemExit(main())
