from pathlib import Path
import csv, shutil

REPO = Path("memory/logs/fitness")
RAW  = REPO/"_raw"
NORM = REPO/"normalized"
OUT  = NORM/"fitness_events.csv"
HEAD = ["timestamp","source","type","metric","value","unit","notes"]

def ensure_dirs():
    RAW.mkdir(parents=True, exist_ok=True)
    NORM.mkdir(parents=True, exist_ok=True)
    if not OUT.exists():
        with OUT.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=HEAD).writeheader()

def copy_raw(src):
    ensure_dirs()
    dst = RAW/src.name
    try: shutil.copy2(src, dst)
    except Exception: pass
    return dst

def write_rows(rows):
    ensure_dirs()
    with OUT.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEAD)
        for r in rows:
            w.writerow({k: r.get(k,"") for k in HEAD})
