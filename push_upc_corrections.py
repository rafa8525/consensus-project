import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Keto classification logic
def classify_keto(description):
    desc = description.lower()
    if any(x in desc for x in ["sugar", "honey", "rice", "pasta", "flour", "corn", "syrup", "fruit"]):
        return "❌ Not Keto"
    elif any(x in desc for x in ["carb", "sweet", "whole wheat"]):
        return "⚠️ Slightly Keto"
    else:
        return "✅ Keto"

# Telegram alert stub (to be replaced with actual webhook/send function)
def alert_failure(upc):
    print(f"⚠️ ALERT: Failed to update row with UPC {upc}.")

# Setup Google Sheets API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open the sheet
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1DV7hWdPpuEiZ03zx-Kop3TdL9LN12QfYtGwdso0-6f8/edit")
worksheet = sheet.worksheet("Sheet1")

# Corrections to apply
corrections = {
    "36000214000": ["Kleenex Ultra Soft", "3-ply facial tissues, cube box"],
    "73852514599": ["Purell Hand Sanitizer", "Advanced formula, 2 fl oz travel bottle"],
    "47495112900": ["Nature’s Bakery Fig Bar", "Whole wheat, twin-pack bar"],
    "755000000010": ["Texas Pete Original Hot Sauce", "6 fl oz bottle, 0 calories per serving, 35 servings per container"],
    "708747151930": ["Gourmet Nut Power Up Trail Mix", "High Energy Mix – Non-GMO, gluten-free snack pack, 14 oz bag"]
}

# Get all values in the sheet
rows = worksheet.get_all_values()
header_offset = 1  # first row is header

# Loop through rows and update matches
for idx, row in enumerate(rows[1:], start=2):  # start=2 because gspread is 1-indexed
    upc = row[0].strip()
    timestamp = row[1].strip() if len(row) > 1 else ""
    name = row[2].strip() if len(row) > 2 else ""
    desc = row[3].strip() if len(row) > 3 else ""
    keto = row[4].strip() if len(row) > 4 else ""

    updated = False

    if upc in corrections:
        correct_name, correct_desc = corrections[upc]

        if not name:
            worksheet.update_cell(idx, 3, correct_name)
            print(f"Updated name for {upc}")
            name = correct_name
            updated = True
        if not desc:
            worksheet.update_cell(idx, 4, correct_desc)
            print(f"Updated description for {upc}")
            desc = correct_desc
            updated = True

    # Alert if missing name or desc
    if upc and timestamp and (not name or not desc):
        alert_failure(upc)

    # Classify keto if name/desc exists but keto field is empty
    if name and desc and not keto:
        keto_status = classify_keto(desc)
        worksheet.update_cell(idx, 5, keto_status)
        print(f"Tagged keto status for {upc}: {keto_status}")

print("\u2705 Barcode Sheet Updated Successfully")
