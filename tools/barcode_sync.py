#!/usr/bin/env python3
import csv, json, re, sys, urllib.request, urllib.error, argparse
from datetime import datetime, date, timezone
from pathlib import Path

BASE  = Path.home() / "consensus-project"
NUT   = BASE / "memory" / "logs" / "nutrition"
STATE = NUT / ".barcode_sync_state.json"
DBG   = NUT / ("barcode_sync_debug_%s.json" % date.today().isoformat())
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
        creds = Credentials.from_service_account_file(str(svc), scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
        ws = gspread.authorize(creds).open_by_key(SHEET_ID).get_worksheet(0)
        rows = ws.get_all_values()
        from io import StringIO
        sio = StringIO(); w = csv.writer(sio)
        for r in rows: w.writerow(r)
        return sio.getvalue()
    except Exception:
        return None

def canon(h: str) -> str:
    h = re.sub(r"[^a-z0-9]+", "_", h.strip().lower())
    return re.sub(r"_+", "_", h).strip("_")

def parse_csv(txt):
    rows = list(csv.reader(txt.splitlines()))
    if not rows: return [], [], {}, [], True
    hdr_raw = rows[0]
    # Force headerless for this sheet shape
    hdr_can = ["barcode","timestamp","item","details","class"]
    idx = {h:i for i,h in enumerate(hdr_can)}
    DBG.write_text(json.dumps({"mode":"forced_headerless","headers_raw":hdr_raw,"headers_canonical":hdr_can}, indent=2), encoding="utf-8")
    return rows, hdr_can, idx, hdr_raw, True

def fnum_unit(s, want_kcal=False):
    if s is None: return 0.0
    t = str(s)
    if want_kcal:
        m = re.search(r'([-+]?\d+(?:[.,]\d+)?)\s*(?:k?cal|calories)\b', t, re.I)
        return float(m.group(1).replace(",", ".")) if m else 0.0
    m = re.search(r'([-+]?\d+(?:[.,]\d+)?)\s*(?:g|gram|grams)\b', t, re.I)
    return float(m.group(1).replace(",", ".")) if m else 0.0

def to_day(s):
    s = (s or "").strip()
    m = re.search(r'(\d{4})[ _\-\/](\d{2})[ _\-\/](\d{2})', s)  # 2025_06_23_...
    if m: return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.search(r'(\d{4}-\d{2}-\d{2})', s)
    if m: return m.group(1)
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', s)
    if m:
        mm, dd, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if yy < 100: yy += 2000
        return f"{yy:04d}-{mm:02d}-{dd:02d}"
    return date.today().isoformat()
def append_barcode_log(d, entries, overwrite=False):
    p = NUT / f"barcode_log_{d}.md"
    lines = [] if overwrite else (p.read_text(encoding="utf-8").splitlines() if p.exists() else [])
    if not lines: lines = [f"# Barcode Log — {d}", ""]
    for e in entries:
        klass = f" [{e['klass']}]" if e.get("klass") else ""
        lines.append(f"- {e['when']} — {e['item']}{klass} — {e['cal']} kcal; P {e['protein_g']}g / F {e['fat_g']}g / NC {e['net_carbs_g']}g (TC {e['carbs_g']}g, Fiber {e['fiber_g']}g)")
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
    ti = next((i for i,ln in enumerate(lines) if ln.strip().startswith("- totals:")), None)
    if ti is None:
        lines.append('- totals: { "cal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "net_carbs_g": 0 }'); ti=len(lines)-1
    t = totals
    lines[ti] = (f'- totals: {{ "cal": {int(t["cal"])}, "protein_g": {round(t["protein_g"],2)}, '
                 f'"fat_g": {round(t["fat_g"],2)}, "carbs_g": {round(t["carbs_g"],2)}, "net_carbs_g": {round(t["net_carbs_g"],2)} }}')
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
def parse_rows(rows, idx):
    grouped = {}
    for row in rows:
        get = lambda key: (row[idx[key]] if key in idx and idx[key] < len(row) else "")
        d     = to_day(get("timestamp"))
        item  = (get("item") or "(unknown)").strip()
        klass = (get("class") or "").strip()
        # Strict: only capture explicit units; ignore stray numbers
        cal   = fnum_unit(get("details"), want_kcal=True)
        prot  = fnum_unit(get("details"))
        fat   = 0.0
        carbs = 0.0
        fiber = 0.0
        net   = max(carbs - fiber, 0.0)
        when  = (get("timestamp") or iso_now()).strip()
        e = {"when":when,"item":item,"klass":klass,"cal":int(cal),
             "protein_g":round(prot,1),"fat_g":round(fat,1),
             "carbs_g":round(carbs,1),"fiber_g":round(fiber,1),"net_carbs_g":round(net,1)}
        g = grouped.setdefault(d, {"entries": [], "totals": {"cal":0,"protein_g":0.0,"fat_g":0.0,"carbs_g":0.0,"net_carbs_g":0.0}})
        g["entries"].append(e)
        t = g["totals"]; t["cal"]+=cal; t["protein_g"]+=prot; t["fat_g"]+=fat; t["carbs_g"]+=carbs; t["net_carbs_g"]+=net
    return grouped
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", help="YYYY-MM-DD to rebuild that day from the sheet (ignores state)")
    args = ap.parse_args()

    # fetch
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

    rows, hdr_can, idx, hdr_raw, _ = parse_csv(txt)
    if not rows:
        print("No sheet rows."); return

    if args.rebuild:
        grouped = parse_rows(rows, idx)
        d = args.rebuild
        pack = grouped.get(d, {"entries": [], "totals": {"cal":0,"protein_g":0.0,"fat_g":0.0,"carbs_g":0.0,"net_carbs_g":0.0}})
        append_barcode_log(d, pack["entries"], overwrite=True)
        set_totals(ensure_nutrition_file(d), pack["totals"])
        DBG.write_text(json.dumps({"mode":"rebuild","headers_raw":hdr_raw,"headers":hdr_can,"idx":idx}, indent=2), encoding="utf-8")
        print(f"Rebuilt {d}: entries={len(pack['entries'])} (mapping in {DBG.name})")
        return

    # incremental
    try: state = json.loads(STATE.read_text(encoding="utf-8"))
    except Exception: state = {"last_row": 0}
    start = max(1, int(state.get("last_row", 0)))
    new_rows = rows[start-1:] if start-1 < len(rows) else []
    grouped = parse_rows(new_rows, idx) if new_rows else {}
    for d, pack in sorted(grouped.items()):
        append_barcode_log(d, pack["entries"])
        set_totals(ensure_nutrition_file(d), pack["totals"])
    state["last_row"] = start + len(new_rows)
    STATE.write_text(json.dumps(state), encoding="utf-8")
    DBG.write_text(json.dumps({"mode":"incremental","headers_raw":hdr_raw,"headers":hdr_can,"idx":idx}, indent=2), encoding="utf-8")
    print(f"Imported rows: {len(new_rows)} days: {len(grouped)} at {iso_now()} (mapping in {DBG.name})")

# --- strict extractors (require a nearby label) ---
def _extract_kcal(text: str) -> float:
    if not text: return 0.0
    m = re.search(r'([-+]?\d+(?:[.,]\d+)?)\s*(?:k?cal|calories)\b', str(text), re.I)
    return float(m.group(1).replace(',', '.')) if m else 0.0

def _extract_macro_g(text: str, kind: str) -> float:
    if not text: return 0.0
    t = str(text)
    kinds = {
        "protein": r'(?:protein|prot\b)',
        "fat":     r'\bfat\b',
        "carbs":   r'(?:carb(?:s)?|carbohydrate(?:s)?)',
        "fiber":   r'(?:fiber|fibre)',
        "net":     r'net\s*carb(?:s)?',
    }
    lab = kinds.get(kind, r'$^')  # never matches if unknown
    # label … number g  OR  number g … label (<= ~10 non-word chars between)
    p1 = re.search(rf'(?i){lab}[^\d]{{0,10}}([-+]?\d+(?:[.,]\d+)?)\s*g', t)
    if p1:
        return float(p1.group(1).replace(',', '.'))
    p2 = re.search(rf'(?i)([-+]?\d+(?:[.,]\d+)?)\s*g[^\w]{{0,10}}{lab}', t)
    return float(p2.group(1).replace(',', '.')) if p2 else 0.0

# --- OVERRIDE: parse_rows now uses strict label-based macros ---
def parse_rows(rows, idx):
    grouped = {}
    for row in rows:
        get = lambda key: (row[idx[key]] if key in idx and idx[key] < len(row) else "")
        d     = to_day(get("timestamp"))
        item  = (get("item") or "(unknown)").strip()
        klass = (get("class") or "").strip()
        details = get("details")

        cal   = _extract_kcal(details)
        prot  = _extract_macro_g(details, "protein")
        fat   = _extract_macro_g(details, "fat")
        carbs = _extract_macro_g(details, "carbs")
        fiber = _extract_macro_g(details, "fiber")
        net   = _extract_macro_g(details, "net")
        if net == 0 and carbs > 0:
            net = max(carbs - fiber, 0.0)

        when  = (get("timestamp") or iso_now()).strip()
        e = {"when":when,"item":item,"klass":klass,"cal":int(cal),
             "protein_g":round(prot,1),"fat_g":round(fat,1),
             "carbs_g":round(carbs,1),"fiber_g":round(fiber,1),"net_carbs_g":round(net,1)}
        g = grouped.setdefault(d, {"entries": [], "totals": {"cal":0,"protein_g":0.0,"fat_g":0.0,"carbs_g":0.0,"net_carbs_g":0.0}})
        g["entries"].append(e)
        t = g["totals"]; t["cal"]+=cal; t["protein_g"]+=prot; t["fat_g"]+=fat; t["carbs_g"]+=carbs; t["net_carbs_g"]+=net
    return grouped

if __name__ == "__main__":
    main()
