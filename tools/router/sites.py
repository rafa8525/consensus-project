import csv, os

def find_sites_csv(candidates):
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def load_sites(candidates):
    path = find_sites_csv(candidates)
    if not path:
        raise FileNotFoundError("support sites CSV not found:\n  " + "\n  ".join(candidates))
    sites = []
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        _ = next(reader, [])  # header (optional)
        for i, row in enumerate(reader, start=2):
            row = [(row[j] if j < len(row) else "").strip() for j in range(4)]
            name, url = None, None
            for item in row:
                if not name and item and not item.startswith("http"):
                    name = item
                elif not url and item.startswith("http"):
                    url = item
            if url:
                if not name:
                    name = f"Agent{i-1}"
                sites.append({"agent": name, "url": url})
    if not sites:
        raise ValueError("parsed 0 sites from CSV: " + path)
    return sites
