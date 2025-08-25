import os, csv, datetime, pathlib

def ensure_parent(path: str):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)

def today_csv_path(base_dir: str) -> str:
    d = datetime.date.today().strftime("%Y-%m-%d")
    return os.path.join(base_dir, f"agent_learnings_{d}.csv")

def append_learnings(path: str, rows):
    newfile = not os.path.exists(path)
    ensure_parent(path)
    with open(path, "a", newline='', encoding="utf-8") as f:
        w = csv.writer(f)
        if newfile:
            w.writerow(["Agent #","Agent Name","Support Site","Query","Learning (Today)","Site HTTP"])
        for r in rows:
            w.writerow(r)
