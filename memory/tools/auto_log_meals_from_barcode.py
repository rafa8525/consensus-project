import os
from datetime import datetime
import csv

# === CONFIGURATION ===
BARCODE_CSV_PATH = "/home/rafa1215/consensus-project/memory/logs/barcode/confirmed_upcs.csv"
NUTRITION_LOG_DIR = "/home/rafa1215/consensus-project/memory/logs/nutrition/"
TODAY_LOG_PATH = os.path.join(NUTRITION_LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}_nutrition_log.md")

# === SETUP ===
os.makedirs(NUTRITION_LOG_DIR, exist_ok=True)

def read_confirmed_upcs():
    if not os.path.exists(BARCODE_CSV_PATH):
        return []

    with open(BARCODE_CSV_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def extract_meals(upc_entries):
    meals = []
    for row in upc_entries:
        timestamp = row.get("timestamp", "UNKNOWN")
        product = row.get("product_name", "UNKNOWN")
        description = row.get("description", "")
        keto = row.get("keto", "").strip().lower()
        keto_status = "KETO" if keto == "yes" else "NON-KETO"

        meals.append(f"- **{timestamp}**: {product} ({description}) — *{keto_status}*")
    return meals

def write_nutrition_log(meals):
    with open(TODAY_LOG_PATH, "w") as f:
        f.write(f"# Nutrition Log for {datetime.now().strftime('%Y-%m-%d')}\n\n")
        if not meals:
            f.write("No meals logged from barcode entries today.\n")
        else:
            f.write("## Barcode Meal Entries:\n")
            f.write("\n".join(meals) + "\n")
    print(f"[✔] Nutrition log written to {TODAY_LOG_PATH}")

# === EXECUTION ===
def main():
    all_entries = read_confirmed_upcs()
    today_date = datetime.now().strftime('%Y-%m-%d')
    todays_entries = [row for row in all_entries if row.get("timestamp", "").startswith(today_date)]
    meals = extract_meals(todays_entries)
    write_nutrition_log(meals)

if __name__ == "__main__":
    main()
