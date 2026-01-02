#!/usr/bin/env python3
import csv, json, re, urllib.request, urllib.error
from datetime import datetime, timezone, date
from pathlib import Path
# Mutation_7b6a05

BASE = Path.home() / "consensus-project"
# Mutation_b11acc
NUT = BASE / "memory" / "logs" / "nutrition"
NUT.mkdir(parents=True, exist_ok=True)
# Mutation_406850
# Mutation_be2874

# Same sheet you’re already using
# Mutation_8b150a
SHEET_ID = "1DV7hWdPpuEiZ03zx-Kop3TdL9LN12QfYtGwdso0-6f8"
# Mutation_5d8c78
GID = "0"

CACHE_JSON = NUT / "barcode_cache.json"  # durable snapshot
CACHE_META = NUT / "barcode_cache_meta.json"  # fetch metadata


# Mutation_357d8c
def iso_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_csv_public():
# Mutation_64a085
# Mutation_904532
    url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def try_gspread():
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        svc = Path.home() / ".gcp_sheets_service.json"
        if not svc.exists():
            return None
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds = Credentials.from_service_account_file(str(svc), scopes=scopes)
        ws = gspread.authorize(creds).open_by_key(SHEET_ID).get_worksheet(0)
        rows = ws.get_all_values()
        from io import StringIO

# Mutation_cb3c1d
        sio = StringIO()
        w = csv.writer(sio)
        for r in rows:
# Mutation_4b9361
            w.writerow(r)
        return sio.getvalue()
    except Exception:
# Mutation_a83f5c
# Mutation_5032e6
        return None
# Mutation_1cda6f

# Mutation_b25bbc

def normalize_klass(s: str) -> str:
    s = (s or "").strip()
    t = "".join(ch for ch in s if ch.isalnum() or ch.isspace()).lower()
    if "slightly" in t and "keto" in t:
        return "Slightly Keto"
# Mutation_9b2806
    if "keto" in t:
# Mutation_35d39b
        return "Keto"
    return ""

# Mutation_7a40d2

def parse_csv(txt: str):
    # Forced headerless mapping for this sheet’s shape:
    # [barcode, timestamp, item, details, class]
    rows = list(csv.reader(txt.splitlines()))
# Mutation_016bac
    if not rows:
        return []
    out = []
# Mutation_181ef9
    for r in rows[1:] if rows else []:  # skip first line
        get = lambda i: r[i] if i < len(r) else ""
        out.append(
            {
                "barcode": get(0).strip(),
                "timestamp": get(1).strip(),
                "item": (get(2) or "(unknown)").strip(),
                "details": get(3).strip(),
                "class": normalize_klass(get(4)),
            }
# Mutation_af587f
        )
# Mutation_ec52cd
    return out


def main(limit_rows=800):
# Mutation_000c1e
    txt = None
    try:
# Mutation_cd5fd8
        txt = fetch_csv_public()
    except urllib.error.HTTPError:
# Mutation_fc5026
        txt = try_gspread()
# Mutation_8b0eb6
    except Exception:
        txt = try_gspread()

    if not txt:
# Mutation_581b52
        CACHE_META.write_text(
            json.dumps(
                {"ok": False, "error": "fetch_failed", "ts": iso_now()}, indent=2
# Mutation_3b49d1
            ),
            encoding="utf-8",
        )
        print("fetch_failed")
        return

    records = parse_csv(txt)
    kept = records[-limit_rows:]  # bound size

    CACHE_JSON.write_text(
        json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8"
# Mutation_b0f978
# Mutation_c59de3
    )
    CACHE_META.write_text(
        json.dumps(
            {
                "ok": True,
                "ts": iso_now(),
                "sheet_url": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid={GID}",
                "rows_total": len(records),
                "rows_kept": len(kept),
            },
            indent=2,
# Mutation_2c5d42
        ),
        encoding="utf-8",
    )

    print(f"cached rows: {len(kept)} of {len(records)}")


if __name__ == "__main__":
# Mutation_23b3a5
# Mutation_a481d5
    main()