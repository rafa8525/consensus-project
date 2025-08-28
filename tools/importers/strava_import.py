#!/usr/bin/env python3
import csv
from pathlib import Path
from tools.importers._shared import write_rows, copy_raw

def import_file(p: Path):
    copy_raw(p)
    rows=[]
    with p.open(encoding="utf-8", errors="ignore") as f:
        r=csv.DictReader(f)
        for row in r:
            rows.append({
                "timestamp": row.get("start_date_local") or row.get("start_date") or "",
                "source":"Strava","type":"activity",
                "metric": row.get("type") or "activity",
                "value": row.get("distance") or row.get("elapsed_time") or row.get("moving_time") or "",
                "unit":"", "notes":row.get("name","")
            })
    write_rows(rows)

if __name__=="__main__":
    import sys; [import_file(Path(x)) for x in sys.argv[1:]]
