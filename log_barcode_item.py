import datetime
from pathlib import Path

def log_barcode_item(upc_code, item_name, keto_status):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/food")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    entry = f"{timestamp} — UPC: {upc_code} — Item: {item_name} — Keto: {keto_status}\n"
    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example: log item manually
    log_barcode_item("755000000010", "Texas Pete Hot Sauce", "Yes")
