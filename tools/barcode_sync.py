#!/usr/bin/env python3
import csv, json, re, sys, urllib.request, urllib.error, argparse
from datetime import datetime, date, timezone
from pathlib import Path

BASE  = Path.home() / "consensus-project"
NUT   = BASE / "memory" / "logs" / "nutrition"
STATE = NUT / ".barcode_sync_state.json"
NUT.mkdir(parents=True, exist_ok=True)

SHEET_ID = "1DV7hWdPpuEiZ03zx-Kop3TdL9LN12QfYtGwdso0-6f8"
GID      = "0"

def iso_now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fetch_csv_public():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def try_gspread():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        svc = Path.home() / ".gcp_sheets_service.json"
        if not svc.exists(): return None
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds = Credentials.from_service_account_file(str(svc), scopes=scopes)
        ws = gspread.authorize(creds).open_by_key(SHEET_ID).get_worksheet(0)
        rows = ws.get_all_values()
        from io import StringIO
        sio = StringIO(); w = csv.writer(sio)
        for r in rows: w.writerow(r)
        return sio.getvalue()
    except Exception:
        return None

def load_state():
    try: return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception: return {"last_row": 0}

def save_state(s): STATE.write_text(json.dumps(s), encoding="utf-8")

def canon(h: str) -> str:
    h = h.strip().lower()
    h = re.sub(r"[^a-z0-9]+", "_", h)
    h = re.sub(r"_+", "_", h).strip("_")
    return h

def parse_csv(txt):
    rows = list(csv.reader(txt.splitlines()))
    if not rows: return [], [], {}
    headers_raw = rows[0]
    headers = [canon(h) for h in headers_raw]
    idx = {h:i for i,h in enumerate(headers)}
    return rows[1:], headers, idx

def find_col(headers, patterns):
    pats = [re.compile(p) for p in patterns]
    for i,h in enumerate(headers):
        for p in pats:
            if p.search(h):
                return i
    return None

def fnum(x):
    if x is None: return 0.0
    s = str(x)
    m = re.search(r'[-+]?\d+(?:[.,]\d+)?', s)
    if not m: return 0.0
    return float(m.group(0).replace(",", "."))

def to_day(s):
    s = (s or "").strip()
    # grab date portion if there's time included
    m = re.search(r'(\d{4}-\d{2}-\d{2})', s)
    if m: return m.group(1)
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', s)  # assume US mm/dd/yyyy
    if m:
        mm, dd, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if yy < 100: yy += 2000
        return f"{yy:04d}-{mm:02d}-{dd:02d}"
    return date.today().isoformat()

def append_barcode_log(d, entries, overwrite=False):
    p = NUT / f"barcode_log_{d}.md"
    lines = [] if overwrite else (p.read_text(encoding="utf-8").splitlines() if p.exists() else [])
    if not lines:
        lines = [f"# Barcode Log — {d}", ""]
    for e in entries:
        lines.append(f"- {e['when']} — {e['item']} — {e['cal']} kcal; P {e['protein_g']}g / F {e['fat_g']}g / NC {e['net_carbs_g']}g (TC {e['carbs_g']}g, Fiber {e['fiber_g']}g)")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")

def ensure_nutrition_file(d):
    p = NUT / f"{d}_nutrition_log.md"
    if not p.exists():
        p.write_text(
            f"# Nutrition — {d}\n- ts: {iso_now()}\n- meals: []\n"
            f'- totals: {{ "cal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "net_carbs_g": 0 }}\n'
            f'- notes: ""\n', encoding="utf-8")
    return p

def set_totals(p, totals):
    lines = p.read_text(encoding="utf-8").splitlines()
    ti = None
    for i,ln in enumerate(lines):
        if ln.strip().startswith("- totals:"):
            ti = i; break
    if ti is None:
        lines.append('- totals: { "cal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "net_carbs_g": 0 }')
        ti = len(lines)-1
    t = totals
    lines[ti] = (f'- totals: {{ "cal": {int(t["cal"])}, "protein_g": {round(t["protein_g"],2)}, '
                 f'"fat_g": {round(t["fat_g"],2)}, "carbs_g": {round(t["carbs_g"],2)}, "net_carbs_g": {round(t["net_carbs_g"],2)} }}')
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")

def build_map(headers):
    # Flexible header detection
    return {
        "date":  find_col(headers, [r"^date$", r"scan_date", r"logged_at", r"timestamp"]),
        "time":  find_col(headers, [r"^time$", r"timestamp", r"logged_at"]),
        "item":  find_col(headers, [r"item", r"product", r"description", r"food", r"name", r"title"]),
        "cal":   find_col(headers, [r"^cal(ories)?$", r"\bkcal\b"]),
        "prot":  find_col(headers, [r"^protein(_g)?$", r"\bprotein\b"]),
        "fat":   find_col(headers, [r"^fat(_g)?$", r"\bfat\b"]),
        "carbs": find_col(headers, [r"^carb(s)?(_g)?$", r"carbo"]),
        "fiber": find_col(headers, [r"^fiber(_g)?$", r"fibre"]),
        "net":   find_col(headers, [r"^net(_)?carb(s)?(_g)?$", r"\bnet\b"]),
    }

def parse_rows(rows, headers):
    col = build_map(headers)
    grouped = {}
    for row in rows:
        get = lambda i: (row[i] if i is not None and i < len(row) else "")
        d = to_day(get(col["date"]))
        item = (get(col["item"]) or "(unknown)").strip()
        cal = fnum(get(col["cal"]))
        prot = fnum(get(col["prot"]))
        fat = fnum(get(col["fat"]))
        carbs = fnum(get(col["carbs"]))
        fiber = fnum(get(col["fiber"]))
        net = fnum(get(col["net"]))
        if net == 0 and carbs > 0:
            net = max(carbs - fiber, 0.0)
        when = (get(col["time"]) or iso_now()).strip()
        e = {"when": when, "item": item, "cal": int(cal),
             "protein_g": round(prot,1), "fat_g": round(fat,1),
             "carbs_g": round(carbs,1), "fiber_g": round(fiber,1),
             "net_carbs_g": round(net,1)}
        g = grouped.setdefault(d, {"entries": [], "totals": {"cal":0,"protein_g":0.0,"fat_g":0.0,"carbs_g":0.0,"net_carbs_g":0.0}})
        g["entries"].append(e)
        t = g["totals"]; t["cal"]+=cal; t["protein_g"]+=prot; t["fat_g"]+=fat; t["carbs_g"]+=carbs; t["net_carbs_g"]+=net
    return grouped

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", help="YYYY-MM-DD to rebuild that day from the sheet (ignores state)")
    args = ap.parse_args()

    txt=None
    try:
        txt = fetch_csv_public()
    except urllib.error.HTTPError as e:
        txt = try_gspread()
        if not txt:
            print(f"ERROR: sheet not public (HTTP {e.code}). Share as 'Anyone with link: Viewer' or add ~/.gcp_sheets_service.json", file=sys.stderr); sys.exit(2)
    except Exception as e:
        txt = try_gspread()
        if not txt:
            print(f"ERROR: cannot fetch sheet: {e}", file=sys.stderr); sys.exit(2)

    rows, headers, idx = parse_csv(txt)
    if not rows:
        print("No sheet rows."); return

    if args.rebuild:
        grouped = parse_rows(rows, headers)
        d = args.rebuild
        pack = grouped.get(d, {"entries": [], "totals": {"cal":0,"protein_g":0.0,"fat_g":0.0,"carbs_g":0.0,"net_carbs_g":0.0}})
        append_barcode_log(d, pack["entries"], overwrite=True)
        nut = ensure_nutrition_file(d)
        set_totals(nut, pack["totals"])
        print(f"Rebuilt {d}: entries={len(pack['entries'])}")
        return

    # incremental mode (stateful)
    state = load_state()
    start = max(1, int(state.get("last_row", 0)))
    new_rows = rows[start-1:] if start-1 < len(rows) else []
    if not new_rows:
        print("No new barcode rows."); return
    grouped = parse_rows(new_rows, headers)
    for d, pack in sorted(grouped.items()):
        append_barcode_log(d, pack["entries"])
        nut = ensure_nutrition_file(d)
        # additive totals (incremental)
        prev = {"cal":0,"protein_g":0.0,"fat_g":0.0,"carbs_g":0.0,"net_carbs_g":0.0}
        set_totals(nut, {k: prev[k] + pack["totals"][k] for k in prev})
    state["last_row"] = start + len(new_rows)
    save_state(state)
    print(f"Imported rows: {len(new_rows)} days: {len(grouped)} at {iso_now()}")
if __name__ == "__main__":
    main()
