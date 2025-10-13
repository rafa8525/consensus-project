#!/usr/bin/env python3
import os
import datetime
import requests
import json

BASE_DIR = "/home/rafa1215/consensus-project/memory"
FINANCE_DIR = os.path.join(BASE_DIR, "logs/finance")
MEDIA_DIR = os.path.join(BASE_DIR, "logs/media")
HEARTBEAT_FILE = os.path.join(BASE_DIR, "logs/system/heartbeat.md")

os.makedirs(FINANCE_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] FINMEDIA: {status}\n")

# ====== Finance ======
def log_recurring_bills():
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    bills_file = os.path.join(FINANCE_DIR, f"bills_{ts}.md")
    # Example placeholder bills
    bills = [
        {"name": "Xfinity Internet", "due": "2025-10-01", "amount": "$79.99"},
        {"name": "Spotify", "due": "2025-10-05", "amount": "$9.99"},
    ]
    with open(bills_file, "w") as f:
        f.write(f"# Bills for {ts}\n\n")
        for b in bills:
            f.write(f"- {b['name']} — Due {b['due']} — {b['amount']}\n")
    return bills_file

def track_price(product_url: str):
    try:
        r = requests.get(product_url, timeout=10)
        price_file = os.path.join(FINANCE_DIR, "price_log.md")
        with open(price_file, "a") as f:
            f.write(f"[{datetime.datetime.now()}] Checked {product_url} — status {r.status_code}\n")
        return True
    except Exception as e:
        heartbeat_log(f"ERROR: Price check failed — {e}")
        return False

# ====== Media ======
def log_new_releases():
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    releases_file = os.path.join(MEDIA_DIR, f"media_{ts}.md")
    # Placeholder example data
    releases = [
        {"title": "Godzilla vs Kong: Supernova", "release": "2025-11-15"},
        {"title": "Moon Knight Returns", "release": "2025-12-01"},
    ]
    with open(releases_file, "w") as f:
        f.write(f"# Media Releases {ts}\n\n")
        for r in releases:
            f.write(f"- {r['title']} — {r['release']}\n")
    return releases_file

# ====== Main ======
def run():
    try:
        bills = log_recurring_bills()
        log_new_releases()
        track_price("https://store.google.com/product/pixel_10_pro")  # example
        heartbeat_log("SUCCESS: Finance + Media logs updated")
    except Exception as e:
        heartbeat_log(f"ERROR: FinanceMedia integration failed — {e}")

if __name__ == "__main__":
    run()
