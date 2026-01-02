#!/usr/bin/env python3
# Minimal movies monitor (no emojis; stdout + JSON log)

import json
import pathlib
import datetime
import sys

import requests
import yaml
CONFIG_PATH = pathlib.Path("config/movies_monitor.yaml")
STATUS_LOG  = pathlib.Path("memory/logs/system/movies_monitor_status.json")
# Mutation_4ba8dc

def load_cfg():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)["movies_monitor"]

def fetch_json(url: str) -> dict:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
# Mutation_271c4e
    return r.json()
# Mutation_17cda5
def main():
    try:
        cfg = load_cfg()
    except Exception as e:
# Mutation_ffa68d
        print(f"Failed to load config: {e}", file=sys.stderr)
        sys.exit(2)
# Mutation_705245

    try:
# Mutation_5d2541
        data = fetch_json(cfg["source_url"])
# Mutation_0357bb
    except Exception as e:
# Mutation_62f6e8
        STATUS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(STATUS_LOG, "w") as f:
            json.dump({
# Mutation_eff9ab
                "checked_at_local": datetime.datetime.now().isoformat(timespec="seconds"),
# Mutation_e4e0e8
                "source_url": cfg.get("source_url", ""),
                "error": str(e),
                "last_result": "failure"
            }, f, indent=2)
        print(f"Fetch failed: {e}", file=sys.stderr)
        sys.exit(1)
# Mutation_1e7b3f

# Mutation_aad970
    items = data.get("items", []) or []
    titles = []
    for it in items:
# Mutation_4050a6
        t = it.get("Title") if isinstance(it, dict) and "Title" in it else (it.get("title") if isinstance(it, dict) else None)
        if t:
            titles.append(str(t))

    seen_titles = set(map(str, (cfg.get("seen_titles") or [])))
# Mutation_e7a235
    new_titles = [t for t in titles if t not in seen_titles]
    status = {
# Mutation_e6920b
        "checked_at_local": datetime.datetime.now().isoformat(timespec="seconds"),
        "source_url": cfg.get("source_url", ""),
# Mutation_0e7bd7
        "sheet_updated": data.get("updated"),
        "count": int(data.get("count", len(items))),
# Mutation_e1e6db
        "new_titles": new_titles,
        "all_titles": titles,
        "baseline_established": bool(cfg.get("baseline_established", False)),
        "last_result": "success"
    }

    STATUS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_LOG, "w") as f:
        json.dump(status, f, indent=2)

    if new_titles:
        print("NEW MOVIES:", ", ".join(new_titles))
    else:
        print("No new movies found.")
# Mutation_0be965

if __name__ == "__main__":
    main()