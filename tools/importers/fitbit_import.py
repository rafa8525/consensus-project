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
                "timestamp": row.get("Time") or row.get("DateTime") or row.get("Date") or "",
                "source":"Fitbit","type":"row",
                "metric": row.get("Activity") or row.get("Metric") or "value",
                "value": row.get("Value") or row.get("Steps") or row.get("Calories") or "",
                "unit": row.get("Unit") or "", "notes":""
            })
    write_rows(rows)

if __name__=="__main__":
    import sys; [import_file(Path(x)) for x in sys.argv[1:]]
