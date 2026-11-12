#!/usr/bin/env python3
"""Cloud-only ACS-03 daily Fitbit snapshot (conservative, idempotent).

Reads authenticated Health Connect export in memory. Writes ONE per-local-day
snapshot to private daily_metrics.jsonl, replacing prior ACS Health Connect
snapshots for same local day; does not touch other sources or days.
Never writes if source quality or freshness is unknown.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone
from health_connect_memory_import import import_candidate

ROOT=Path("/home/rafa1215/consensus-project")
OUTPUT=ROOT/"memory/logs/fitness/daily_metrics.jsonl"
TAG="health_connect_fitbit_snapshot_v1"

def publish(candidate,output=OUTPUT,now=None):
    now=now or datetime.now(timezone.utc)
    q=candidate["quality"]
    if q.get("status")!="SAFE_SOURCE_ONLY" or not q.get("safe"):
        raise ValueError("Unsafe source quality")
    latest=q.get("latest_end_ms")
    if type(latest) is not int or not 0 <= (now.timestamp()*1000-latest) <= 48*3600*1000:
        raise ValueError("Source measurement is stale or in future")
    local_date=q.get("local_date")
    if not isinstance(local_date,str) or len(local_date)!=10:
        raise ValueError("Local date unavailable")
    steps=q.get("total")
    if type(steps) is not int or not 0 <= steps <= 100000:
        raise ValueError("Step total outside bounds")
    row={"timestamp":now.isoformat(),"date_local":local_date,"timezone":"America/Los_Angeles",
         "source":TAG,"source_app_package":q.get("source_package"),
         "steps":steps,"source_records":q["records"],
         "measurement_end_utc":datetime.fromtimestamp(latest/1000,timezone.utc).isoformat(),
         "coverage":"partial_day_fitbit_only","watch_identity_verified":False}
    # Guard path: do not follow symlinks or overwrite unexpected non-files.
    if output.is_symlink() or (output.exists() and not output.is_file()):
        raise ValueError("Unsafe output path")
    output.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    original=[]
    if output.is_file():
        for line in output.read_text(encoding="utf-8").splitlines():
            if not line.strip():continue
            obj=json.loads(line)
            if not isinstance(obj,dict):
                raise ValueError("Unexpected historical record")
            if obj.get("source")==TAG and obj.get("date_local")==local_date:
                continue
            original.append(obj)
    original.append(row)
    filename=None
    try:
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=output.parent,
                                         prefix=".hc-metrics-",delete=False) as fp:
            filename=Path(fp.name)
            os.chmod(filename,0o600)
            for item in original:
                fp.write(json.dumps(item,sort_keys=True)+"\n")
            fp.flush()
            os.fsync(fp.fileno())
        os.replace(filename,output)
    finally:
        if filename is not None:filename.unlink(missing_ok=True)
    return {"local_date":local_date,"records":q["records"],"steps":steps,"path":str(output)}

def main():
    try:
        candidate=import_candidate()
        publish(candidate)
    except Exception as exc:
        print("ACS03_DAILY_PUBLISH=FAIL "+type(exc).__name__)
        return 2
    print("ACS03_DAILY_PUBLISH=PASS")
    print("LOCAL_FITBIT_SOURCE_ONLY=YES")
    print("FULL_DAY_COVERAGE_VERIFIED=NO")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
