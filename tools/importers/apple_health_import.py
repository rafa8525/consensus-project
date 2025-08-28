#!/usr/bin/env python3
from pathlib import Path
from xml.etree import ElementTree as ET
from tools.importers._shared import write_rows, copy_raw

def import_file(p: Path):
    copy_raw(p)
    rows=[]
    try:
        root=ET.parse(p).getroot()
        for rec in root.findall("Record"):
            rows.append({
                "timestamp": rec.get("startDate") or rec.get("creationDate") or "",
                "source":"AppleHealth","type":"record",
                "metric": rec.get("type",""),
                "value": rec.get("value",""),
                "unit": rec.get("unit",""),
                "notes":""
            })
    except Exception:
        pass
    write_rows(rows)

if __name__=="__main__":
    import sys; [import_file(Path(x)) for x in sys.argv[1:]]
