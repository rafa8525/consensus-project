#!/usr/bin/env python3
import csv, json, re, urllib.request, urllib.error
from datetime import datetime, timezone, date
from pathlib import Path

BASE = Path.home() / "consensus-project"
NUT  = BASE / "memory" / "logs" / "nutrition"
NUT.mkdir(parents=True, exist_ok=True)

# Same sheet you’re already using
SHEET_ID = "1DV7hWdPpuEiZ03zx-Kop3TdL9LN12QfYtGwdso0-6f8"
GID      = "0"

CACHE_JSON = NUT / "barcode_cache.json"          # durable snapshot
CACHE_META = NUT / "barcode_cache_meta.json"     # fetch metadata
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
        creds  = Credentials.from_service_account_file(str(svc), scopes=scopes)
        ws     = gspread.authorize(creds).open_by_key(SHEET_ID).get_worksheet(0)
        rows   = ws.get_all_values()
        from io import StringIO
        sio = StringIO(); w = csv.writer(sio)
        for r in rows: w.writerow(r)
        return sio.getvalue()
    except Exception:
        return None
def normalize_klass(s: str) -> str:
    s = (s or "").strip()
    t = "".join(ch for ch in s if ch.isalnum() or ch.isspace()).lower()
    if "slightly" in t and "keto" in t: return "Slightly Keto"
    if "keto" in t: return "Keto"
    return ""

def parse_csv(txt: str):
    # Forced headerless mapping for this sheet’s shape:
    # [barcode, timestamp, item, details, class]
    rows = list(csv.reader(txt.splitlines()))
    if not rows: return []
    out = []
    for r in rows[1:] if rows else []:  # skip first line
        get = lambda i: r[i] if i < len(r) else ""
        out.append({
            "barcode":   get(0).strip(),
            "timestamp": get(1).strip(),
            "item":      (get(2) or "(unknown)").strip(),
            "details":   get(3).strip(),
            "class":     normalize_klass(get(4)),
        })
    return out
def main(limit_rows=800):
    txt = None
    try:
        txt = fetch_csv_public()
    except urllib.error.HTTPError:
        txt = try_gspread()
    except Exception:
        txt = try_gspread()

    if not txt:
        CACHE_META.write_text(json.dumps({
            "ok": False, "error": "fetch_failed", "ts": iso_now()
        }, indent=2), encoding="utf-8")
        print("fetch_failed"); return

    records = parse_csv(txt)
    kept = records[-limit_rows:]  # bound size

    CACHE_JSON.write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8")
    CACHE_META.write_text(json.dumps({
        "ok": True,
        "ts": iso_now(),
        "sheet_url": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid={GID}",
        "rows_total": len(records),
        "rows_kept": len(kept)
    }, indent=2), encoding="utf-8")

    print(f"cached rows: {len(kept)} of {len(records)}")

if __name__ == "__main__":
    main()
