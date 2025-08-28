#!/usr/bin/env python3
import json, csv
from pathlib import Path
from tools.importers._shared import write_rows, copy_raw

def parse_json(p: Path):
    rows=[]
    try:
        data=json.loads(p.read_text(encoding="utf-8"))
        buckets=data.get("bucket",[])
        for b in buckets:
            for ds in b.get("dataset",[]):
                for pt in ds.get("point",[]):
                    ts = pt.get("startTimeNanos","")
                    ts = (ts and ts[:-9]) or ""  # ns->s
                    dt = ts and __import__("datetime").datetime.utcfromtimestamp(int(ts)).isoformat() or ""
                    val=None
                    if pt.get("value"):
                        v=pt["value"][0]
                        val = v.get("fpVal") or v.get("intVal") or ""
                    rows.append({"timestamp":dt,"source":"GoogleFit","type":"point",
                                 "metric":pt.get("dataTypeName",""),"value":val,"unit":"","notes":""})
    except Exception: pass
    return rows

def parse_csv(p: Path):
    rows=[]
    with p.open(encoding="utf-8", errors="ignore") as f:
        r=csv.DictReader(f)
        for row in r:
            rows.append({
                "timestamp": row.get("Start time") or row.get("Date") or row.get("Time") or "",
                "source":"GoogleFit","type":"row",
                "metric": row.get("Data type") or row.get("Activity type") or "value",
                "value": row.get("Value") or row.get("Steps") or row.get("Duration (ms)") or "",
                "unit": row.get("Unit") or "", "notes":""
            })
    return rows

def import_file(p: Path):
    copy_raw(p)
    if p.suffix.lower()==".json": rows = parse_json(p)
    else: rows = parse_csv(p)
    write_rows(rows)

if __name__=="__main__":
    import sys; [import_file(Path(x)) for x in sys.argv[1:]]
