#!/usr/bin/env python3
from pathlib import Path
import csv, shutil
OUT = Path("memory/logs/fitness/normalized/fitness_events.csv")
if not OUT.exists():
    print("No normalized CSV."); raise SystemExit(0)
seen=set()
tmp = OUT.with_suffix(".tmp")
with OUT.open(newline="", encoding="utf-8") as fin, tmp.open("w", newline="", encoding="utf-8") as fout:
    r = csv.reader(fin); w = csv.writer(fout)
    header = next(r, None)
    if header: w.writerow(header)
    for row in r:
        key = tuple(row)
        if key in seen: continue
        seen.add(key); w.writerow(row)
shutil.move(tmp, OUT)
print(f"Kept {len(seen)} unique rows.")
