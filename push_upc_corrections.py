#!/usr/bin/env python3
# push_upc_corrections.py
# Backfills Product Name & Description (Open Food Facts) and writes Column E: Keto / Slightly Keto / Not Keto.
# Auth supports Service Account (preferred) or OAuth client+token (fallback).

import os, time, logging
from typing import Optional, Tuple

# ===== CONFIG =====
# Open by ID first (your sheet ID from the URL)
SHEET_ID         = os.getenv("SHEET_ID", "1DV7hWdPpuEiZ03zx-Kop3TdL9LN12QfYtGwdso0-6f8")
# Fallbacks if ID isn't set or accessible:
SHEET_NAME       = os.getenv("SHEET_NAME", "barcode_log_sheet")
WORKSHEET_NAME   = os.getenv("WORKSHEET_NAME", "Sheet1")

# Credentials (absolute paths recommended)
CREDENTIALS_JSON = os.getenv("CREDENTIALS_JSON", "/home/rafa1215/consensus-project/credentials.json")
TOKEN_JSON       = os.getenv("TOKEN_JSON", "/home/rafa1215/consensus-project/token.json")

OPENFOODFACTS_TIMEOUT = float(os.getenv("OFF_TIMEOUT", "6.0"))
USER_AGENT = os.getenv("USER_AGENT", "RafaelBarcodeKeto/1.0 (PythonAnywhere)")

# Columns A..E
COL_BARCODE = 1
COL_TIMESTAMP = 2
COL_NAME = 3
COL_DESC = 4
COL_KETO = 5

# Plain-text tags
TAG_KETO   = "Keto"
TAG_SLIGHT = "Slightly Keto"
TAG_NOT    = "Not Keto"

# Stamp last run to this cell (set to "" to disable)
LAST_RUN_CELL = os.getenv("LAST_RUN_CELL", "Z1")
# ===================

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

KEYWORDS_NOT_KETO = [
    "sugar","cane sugar","corn syrup","high fructose","honey","agave","molasses",
    "flour","enriched wheat","rice","pasta","noodle","bread","tortilla","cracker",
    "banana","mango","pineapple","grape","apple juice","orange juice","brown sugar",
    "oat","granola","barley","maltodextrin","dextrose","glucose","sucrose"
]
KEYWORDS_KETO = [
    "zero sugar","unsweetened","no sugar added","monk fruit","stevia","erythritol",
    "xylitol","coconut oil","mct","almond","pecan","pistachio","walnut",
    "pork rinds","chicharrones","olive oil","avocado oil"
]

def classify_from_description(desc: str) -> Optional[str]:
    if not desc:
        return None
    t = desc.lower()
    if any(kw in t for kw in KEYWORDS_NOT_KETO):
        return TAG_NOT
    if any(kw in t for kw in KEYWORDS_KETO):
        return TAG_KETO
    return TAG_SLIGHT

def fetch_off_by_barcode(barcode: str) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    try:
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=OPENFOODFACTS_TIMEOUT)
        if r.status_code != 200:
            return None, None, None
        product = (r.json() or {}).get("product") or {}
        name = product.get("product_name") or product.get("product_name_en")
        ingredients_text = product.get("ingredients_text") or product.get("ingredients_text_en")
        nutr = product.get("nutriments") or {}
        carbs = nutr.get("carbohydrates_100g")
        try:
            carbs = float(carbs) if isinstance(carbs, str) else carbs
        except Exception:
            carbs = None
        return name, ingredients_text, carbs
    except Exception:
        return None, None, None

def classify_from_carbs(carbs_100g: Optional[float]) -> Optional[str]:
    if carbs_100g is None:
        return None
    if carbs_100g <= 8.0:
        return TAG_KETO
    if 8.0 < carbs_100g <= 11.0:
        return TAG_SLIGHT
    return TAG_NOT

def _authorize():
    scopes = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_JSON, scopes)
        gc = gspread.authorize(creds)
        logging.info("Auth: Service Account")
        return gc
    except Exception as e:
        if "Unexpected credentials type" in str(e) or "service_account" in str(e).lower():
            from gspread import oauth
            gc = oauth(credentials_filename=CREDENTIALS_JSON, authorized_user_filename=TOKEN_JSON)
            logging.info("Auth: OAuth (token.json)")
            return gc
        raise

def open_sheet():
    gc = _authorize()
    sh = None

    # Try by ID first (robust to title changes)
    if SHEET_ID:
        try:
            sh = gc.open_by_key(SHEET_ID)
            logging.info(f"Opened by ID: {SHEET_ID}")
        except Exception as e:
            logging.warning(f"Open by ID failed: {e}")

    # Fallback: open by title
    if sh is None:
        sh = gc.open(SHEET_NAME)
        logging.info(f"Opened by title: {SHEET_NAME}")

    # Try named worksheet; fallback to first sheet if not found
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except Exception:
        ws = sh.get_worksheet(0)
        logging.info(f"Worksheet '{WORKSHEET_NAME}' not found; using first sheet: '{ws.title}'")

    return sh, ws

def main():
    sh, ws = open_sheet()
    values = ws.get_all_values()
    if not values:
        logging.info("Sheet is empty.")
        # Still stamp a run so you can see it executed
        if LAST_RUN_CELL:
            try:
                ws.update_acell(LAST_RUN_CELL, f"Last keto tag run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception:
                pass
        return

    wrote = 0
    for idx, row in enumerate(values[1:], start=2):
        try:
            barcode = (row[COL_BARCODE-1] or "").strip()
            if not barcode:
                continue

            name = (row[COL_NAME-1] or "").strip()
            desc = (row[COL_DESC-1] or "").strip()
            keto = (row[COL_KETO-1] or "").strip()

            # Skip if already classified
            if keto in (TAG_KETO, TAG_SLIGHT, TAG_NOT):
                continue

            tag = classify_from_description(desc)

            off_name = off_desc = None
            off_carbs = None
            if not name or not desc or tag is None:
                off_name, off_desc, off_carbs = fetch_off_by_barcode(barcode)
                if not name and off_name:
                    ws.update_cell(idx, COL_NAME, off_name); name = off_name
                if not desc and off_desc:
                    ws.update_cell(idx, COL_DESC, off_desc); desc = off_desc
                if tag is None:
                    tag = classify_from_carbs(off_carbs)

            if tag is None:
                tag = TAG_SLIGHT

            ws.update_cell(idx, COL_KETO, tag)
            wrote += 1
            time.sleep(0.25)  # be gentle with API quotas
        except Exception as e:
            logging.error(f"Row {idx} failed: {e}")

    # Health stamp
    if LAST_RUN_CELL:
        try:
            ws.update_acell(LAST_RUN_CELL, f"Last keto tag run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception:
            pass

    print(f"Done. Updated {wrote} row(s).")

if __name__ == "__main__":
    main()
