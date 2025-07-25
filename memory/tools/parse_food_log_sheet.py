import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# === CONFIG ===
SHEET_ID = "1DV7hWdPpuEiZ03zx-Kop3TdL9LN12QfYtGwdso0-6f8"
SHEET_NAME = "Sheet1"  # Adjust if renamed
DEST_DIR = "/home/rafa1215/consensus-project/memory/logs/food/"

# === SETUP ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/home/rafa1215/.gdrive/credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

rows = sheet.get_all_records()

today_str = datetime.now().strftime("%Y-%m-%d")
md_filename = f"{DEST_DIR}{today_str}.md"

entries = []
for row in rows:
    timestamp = row.get("Timestamp") or ""
    upc = row.get("UPC") or ""
    product = row.get("Product Name") or ""
    keto = row.get("Keto?") or ""
    notes = row.get("Notes") or ""

    entries.append(f"- {timestamp} | UPC: `{upc}` | {product} | Keto: **{keto}** | Notes: {notes}")

if entries:
    with open(md_filename, "w") as f:
        f.write(f"# Food Log for {today_str}\n\n")
        f.write("\n".join(entries))

    print(f"[✔] Synced food log to {md_filename}")
else:
    print("[✘] No entries found in Google Sheet.")
