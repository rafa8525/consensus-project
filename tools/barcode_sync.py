#!/usr/bin/env python3
import csv, json, re, sys, urllib.request, urllib.error
from datetime import datetime, date, timezone
from pathlib import Path

BASE = Path.home() / "consensus-project"
NUT  = BASE / "memory" / "logs" / "nutrition"
STATE= NUT / ".barcode_sync_state.json"
NUT.mkdir(parents=True, exist_ok=True)

SHEET_ID = "1DV7hWdPpuEiZ03zx-Kop3TdL9LN12QfYtGwdso0-6f8"  # your sheet
GID      = "0"                                          # first tab

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
        gc = gspread.authorize(creds)
        ws = gc.open_by_key(SHEET_ID).get_worksheet(0)
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

def norm(h): return re.sub(r"[^a-z0-9]+","_", h.strip().lower())
def parse_csv(txt):
    rows = list(csv.reader(txt.splitlines()))
    if not rows: return [], {}
    headers = [norm(h) for h in rows[0]]
    idx = {h:i for i,h in enumerate(headers)}
    return rows[1:], idx

def fnum(x):
    try:
        if isinstance(x,str): x=x.strip().replace(",",".")
        return float(x)
    except: return 0.0

def pick(row, idx, *keys):
    for k in keys:
        i = idx.get(k)
        if i is not None and i < len(row) and row[i] != "":
            return row[i]
    return ""

def to_day(s):
    s=(s or "").strip()
    for fmt in ("%Y-%m-%d","%m/%d/%Y","%d/%m/%Y","%Y/%m/%d"):
        try: return datetime.strptime(s, fmt).date().isoformat()
        except: pass
    return date.today().isoformat()

def append_barcode_log(d, entries):
    p = NUT / f"barcode_log_{d}.md"
    lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    if not lines: lines=[f"# Barcode Log — {d}",""]
    for e in entries:
        lines.append(f"- {e['when']} — {e['item']} — {e['cal']} kcal; P {e['protein_g']}g / F {e['fat_g']}g / NC {e['net_carbs_g']}g (TC {e['carbs_g']}g, Fiber {e['fiber_g']}g)")
    p.write_text("\n".join(lines)+"\n", encoding="utf-8")

def ensure_nutrition_file(d):
    p = NUT / f"{d}_nutrition_log.md"
    if not p.exists():
        p.write_text(
            f"# Nutrition — {d}\n"
            f"- ts: {iso_now()}\n- meals: []\n"
            f'- totals: {{ "cal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "net_carbs_g": 0 }}\n'
            f'- notes: ""\n', encoding="utf-8")
    return p

def update_totals(p, add):
    import re
    lines = p.read_text(encoding="utf-8").splitlines()
    ti=None
    for i,ln in enumerate(lines):
        if ln.strip().startswith("- totals:"): ti=i; break
    if ti is None:
        lines.append('- totals: { "cal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "net_carbs_g": 0 }'); ti=len(lines)-1
    def extract(s):
        m=re.findall(r'([a-z_]+)\s*:\s*([0-9]+(?:\.[0-9]+)?)', s)
        d={k:float(v) for k,v in m}
        return {"cal":d.get("cal",0),"protein_g":d.get("protein_g",0),"fat_g":d.get("fat_g",0),
                "carbs_g":d.get("carbs_g",0),"net_carbs_g":d.get("net_carbs_g",0)}
    cur=extract(lines[ti])
    for k in cur: cur[k]=round(cur[k]+add.get(k,0),2)
    lines[ti]=(f'- totals: {{ "cal": {int(cur["cal"])}, "protein_g": {cur["protein_g"]}, '
               f'"fat_g": {cur["fat_g"]}, "carbs_g": {cur["carbs_g"]}, "net_carbs_g": {cur["net_carbs_g"]} }}')
    p.write_text("\n".join(lines)+"\n", encoding="utf-8")

def main():
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

    rows, idx = parse_csv(txt)
    if not rows: 
        print("No sheet rows."); return

    state = load_state()
    start = max(1, int(state.get("last_row", 0)))
    new_rows = rows[start-1:] if start-1 < len(rows) else []
    if not new_rows:
        print("No new barcode rows."); return

    grouped={}
    for i,row in enumerate(new_rows, start=start):
        d = to_day(pick(row, idx, "date","scan_date","logged_at","timestamp"))
        item = pick(row, idx, "item","product","description","food") or "(unknown)"
        cal  = fnum(pick(row, idx, "calories","cal","kcal"))
        prot = fnum(pick(row, idx, "protein_g","protein","protein__g_"))
        fat  = fnum(pick(row, idx, "fat_g","fat","fat__g_"))
        carbs= fnum(pick(row, idx, "carbs_g","carbs","carbohydrate","total_carbs"))
        fiber= fnum(pick(row, idx, "fiber_g","fiber"))
        net  = fnum(pick(row, idx, "net_carbs_g","net_carbs","net")) or max(carbs-fiber,0.0)
        when = pick(row, idx, "time","timestamp","logged_at") or iso_now()
        e={"when":when,"item":item,"cal":int(cal),"protein_g":round(prot,1),"fat_g":round(fat,1),
           "carbs_g":round(carbs,1),"fiber_g":round(fiber,1),"net_carbs_g":round(net,1)}
        grouped.setdefault(d, {"entries":[], "totals":{"cal":0,"protein_g":0.0,"fat_g":0.0,"carbs_g":0.0,"net_carbs_g":0.0}})
        grouped[d]["entries"].append(e)
        g=grouped[d]["totals"]; g["cal"]+=cal; g["protein_g"]+=prot; g["fat_g"]+=fat; g["carbs_g"]+=carbs; g["net_carbs_g"]+=net
        state["last_row"] = i+1

    for d,pack in sorted(grouped.items()):
        append_barcode_log(d, pack["entries"])
        nut=ensure_nutrition_file(d)
        update_totals(nut, pack["totals"])

    save_state(state)
    print(f"Imported rows: {len(new_rows)} days: {len(grouped)} at {iso_now()}")
if __name__ == "__main__":
    main()
