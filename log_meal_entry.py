import datetime
from pathlib import Path

def log_meal_entry(meal_type, description, keto_status):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/food")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    entry = f"{timestamp} — Meal: {meal_type} — {description} — Keto: {keto_status}\n"
    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example: log a lunch
    log_meal_entry("Lunch", "Tuna with avocado", "Yes")
