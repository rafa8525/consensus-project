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
                "timestamp": row.get("Start time") or row.get("create_time") or row.get("Date") or "",
                "source":"SamsungHealth","type":"row",
                "metric": row.get("Data type") or row.get("name") or "value",
                "value": row.get("Value") or row.get("count") or row.get("step_count") or "",
                "unit": row.get("Unit") or "", "notes":""
            })
    write_rows(rows)

if __name__=="__main__":
    import sys; [import_file(Path(x)) for x in sys.argv[1:]]
