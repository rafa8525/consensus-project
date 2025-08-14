#!/usr/bin/env python3
import csv, json, re, sys, urllib.request, urllib.error, argparse, statistics as stats
from datetime import datetime, date, timezone
from pathlib import Path

BASE  = Path.home() / "consensus-project"
NUT   = BASE / "memory" / "logs" / "nutrition"
STATE = NUT / ".barcode_sync_state.json"
DBG   = NUT / ("barcode_sync_debug_%s.json" % date.today().isoformat())
NUT.mkdir(parents=True, exist_ok=True)

SHEET_ID = "1DV7hWdPpuEiZ03zx-Kop3TdL9LN12QfYtGwdso0-6f8"
GID      = "0"

def iso_now(): 
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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

def save_state(s): 
    STATE.write_text(json.dumps(s), encoding="utf-8")

def canon(h: str) -> str:
    h = h.strip().lower()
    h = re.sub(r"[^a-z0-9]+", "_", h)
    h = re.sub(r"_+", "_", h).strip("_")
    return h

def parse_csv(txt):
    rows = list(csv.reader(txt.splitlines()))
    if not rows: return [], [], {}, []
    headers_raw = rows[0]
    headers = [canon(h) for h in headers_raw]
    idx = {h:i for i,h in enumerate(headers)}
    return rows[1:], headers, idx, headers_raw

def fnum(x):
    if x is None: return 0.0
    s = str(x)
    m = re.search(r'[-+]?\d+(?:[.,]\d+)?', s)
    if not m: return 0.0
    try: return float(m.group(0).replace(",", "."))
    except: return 0.0

def to_day(s):
    s = (s or "").strip()
    m = re.search(r'(\d{4}-\d{2}-\d{2})', s)
    if m: return m.group(1)
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', s)  # US-style fallback
    if m:
        mm, dd, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if yy < 100: yy += 2000
        return f"{yy:04d}-{mm:02d}-{dd:02d}"
    return date.today().isoformat()
def profile_columns(rows):
    cols = {}
    if not rows: return cols
    width = max(len(r) for r in rows)
    for i in range(width):
        vals = [r[i] if i < len(r) else "" for r in rows[:200]]
        nums = [fnum(v) for v in vals if fnum(v) != 0.0]
        texts = [v for v in vals if isinstance(v, str) and re.search(r'[A-Za-z]', v)]
        cols[i] = {
            "nonempty": sum(1 for v in vals if str(v).strip() != ""),
            "num_cnt": len(nums),
            "num_avg": (stats.mean(nums) if nums else 0.0),
            "text_cnt": len(texts),
            "sample_text": (texts[0][:40] if texts else "")
        }
    return cols

def find_idx(headers, rx_list):
    pats = [re.compile(p) for p in rx_list]
    for i,h in enumerate(headers):
        if any(p.search(h) for p in pats):
            return i
    return None

def infer_map(rows, headers):
    prof = profile_columns(rows)
    mapping = {
        "date":  find_idx(headers, [r"^date$", r"scan_date", r"logged_at", r"timestamp"]),
        "time":  find_idx(headers, [r"^time$", r"timestamp", r"logged_at"]),
        "item":  find_idx(headers, [r"item", r"product", r"description", r"food", r"name", r"title"]),
        "cal":   find_idx(headers, [r"^cal(ories)?$", r"\bkcal\b"]),
        "prot":  find_idx(headers, [r"^protein(_g)?$", r"\bprotein\b"]),
        "fat":   find_idx(headers, [r"^fat(_g)?$", r"\bfat\b"]),
        "carbs": find_idx(headers, [r"^carb(s)?(_g)?$", r"carbo"]),
        "fiber": find_idx(headers, [r"^fiber(_g)?$", r"fibre"]),
        "net":   find_idx(headers, [r"^net(_)?carb(s)?(_g)?$", r"\bnet\b"]),
    }
    used = set(i for i in mapping.values() if i is not None)

    # text-heavy column as item
    if mapping["item"] is None:
        cand = sorted((i for i in prof if i not in used),
                      key=lambda i: (prof[i]["text_cnt"], -prof[i]["num_cnt"], prof[i]["num_avg"]),
                      reverse=True)
        mapping["item"] = cand[0] if cand else None
        if mapping["item"] is not None: used.add(mapping["item"])

    # calories: highest reasonable numeric
    if mapping["cal"] is None:
        cand = [i for i in prof if i not in used and 30 <= prof[i]["num_avg"] <= 1500 and prof[i]["num_cnt"] > 0]
        cand.sort(key=lambda i: prof[i]["num_avg"], reverse=True)
        mapping["cal"] = cand[0] if cand else None
        if mapping["cal"] is not None: used.add(mapping["cal"])

    # macros
    for key in ("prot","fat","carbs","fiber"):
        if mapping[key] is None:
            cand = [i for i in prof if i not in used and 0 < prof[i]["num_avg"] <= 200 and prof[i]["num_cnt"] > 0]
            cand.sort(key=lambda i: prof[i]["num_avg"], reverse=True)
            mapping[key] = cand[0] if cand else None
            if mapping[key] is not None: used.add(mapping[key])

    DBG.write_text(json.dumps({
        "headers_canonical": headers,
        "column_profiles": prof,
        "inferred_mapping": mapping
    }, indent=2), encoding="utf-8")
    return mapping
def append_barcode_log(d, entries, overwrite=False):
    p = NUT / f"barcode_log_{d}.md"
    lines = [] if overwrite else (p.read_text(encoding="utf-8").splitlines() if p.exists() else [])
    if not lines: lines = [f"# Barcode Log — {d}", ""]
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
        if ln.strip().startswith("- totals:"): ti = i; break
    if ti is None:
        lines.append('- totals: { "cal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "net_carbs_g": 0 }'); ti=len(lines)-1
    t = totals
    lines[ti] = (f'- totals: {{ "cal": {int(t["cal"])}, "protein_g": {round(t["protein_g"],2)}, '
                 f'"fat_g": {round(t["fat_g"],2)}, "carbs_g": {round(t["carbs_g"],2)}, "net_carbs_g": {round(t["net_carbs_g"],2)} }}')
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")

def parse_rows(rows, headers, mapping):
    get = lambda r,i: (r[i] if i is not None and i < len(r) else "")
    grouped = {}
    for row in rows:
        d = to_day(get(row, mapping.get("date")))
        item = (get(row, mapping.get("item")) or "(unknown)").strip()
        cal  = fnum(get(row, mapping.get("cal")))
        prot = fnum(get(row, mapping.get("prot")))
        fat  = fnum(get(row, mapping.get("fat")))
        carbs= fnum(get(row, mapping.get("carbs")))
        fiber= fnum(get(row, mapping.get("fiber")))
        net  = fnum(get(row, mapping.get("net")))
        if net == 0 and carbs > 0: net = max(carbs - fiber, 0.0)
        when = (get(row, mapping.get("time")) or iso_now()).strip()
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
    try: txt = fetch_csv_public()
    except urllib.error.HTTPError as e:
        txt = try_gspread()
        if not txt:
            print(f"ERROR: sheet not public (HTTP {e.code}). Share as 'Anyone with link: Viewer' or add ~/.gcp_sheets_service.json", file=sys.stderr); sys.exit(2)
    except Exception as e:
        txt = try_gspread()
        if not txt:
            print(f"ERROR: cannot fetch sheet: {e}", file=sys.stderr); sys.exit(2)

    rows, headers, idx, headers_raw = parse_csv(txt)
    if not rows:
        print("No sheet rows."); return

    mapping = infer_map(rows, headers)

    if args.rebuild:
        grouped = parse_rows(rows, headers, mapping)
        d = args.rebuild
        pack = grouped.get(d, {"entries": [], "totals": {"cal":0,"protein_g":0.0,"fat_g":0.0,"carbs_g":0.0,"net_carbs_g":0.0}})
        append_barcode_log(d, pack["entries"], overwrite=True)
        set_totals(ensure_nutrition_file(d), pack["totals"])
        print(f"Rebuilt {d}: entries={len(pack['entries'])} (mapping in {DBG.name})")
        return

    state = load_state()
    start = max(1, int(state.get("last_row", 0)))
    new_rows = rows[start-1:] if start-1 < len(rows) else []
    grouped = parse_rows(new_rows, headers, mapping) if new_rows else {}
    for d, pack in sorted(grouped.items()):
        append_barcode_log(d, pack["entries"])
        set_totals(ensure_nutrition_file(d), pack["totals"])
    state["last_row"] = start + len(new_rows)
    save_state(state)
    print(f"Imported rows: {len(new_rows)} days: {len(grouped)} at {iso_now()} (mapping in {DBG.name})")

if __name__ == "__main__":
    main()
