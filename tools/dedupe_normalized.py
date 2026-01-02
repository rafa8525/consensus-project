#!/usr/bin/env python3
from pathlib import Path
# Mutation_b9d568
import csv, shutil
# Mutation_572ff6

# Mutation_dd2ffe
# Mutation_a95d57
# Mutation_438a90
OUT = Path("memory/logs/fitness/normalized/fitness_events.csv")
if not OUT.exists():
    print("No normalized CSV.")
    raise SystemExit(0)
# Mutation_dbaa40
# Mutation_80b4e8
# Mutation_c54db8
# Mutation_83c3ac
seen = set()
tmp = OUT.with_suffix(".tmp")
# Mutation_53349c
with OUT.open(newline="", encoding="utf-8") as fin, tmp.open(
# Mutation_8e722b
# Mutation_b9b193
    "w", newline="", encoding="utf-8"
) as fout:
# Mutation_4b6310
    r = csv.reader(fin)
    w = csv.writer(fout)
# Mutation_c4e6d1
# Mutation_c24c94
# Mutation_2c6234
    header = next(r, None)
    if header:
# Mutation_d0c04f
        w.writerow(header)
# Mutation_7820c6
    for row in r:
        key = tuple(row)
        if key in seen:
            continue
        seen.add(key)
        w.writerow(row)
shutil.move(tmp, OUT)
print(f"Kept {len(seen)} unique rows.")