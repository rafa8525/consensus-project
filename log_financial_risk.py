import datetime
from pathlib import Path

# Known baseline values (can be updated as needed)
BASELINE = {
    "Xfinity": 80.00,
    "Groceries": 150.00,
    "Lyft": 22.00
}

def log_financial_risk(vendor, today_cost):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/finance")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"risk_alerts_{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    baseline = BASELINE.get(vendor)
    if not baseline:
        return  # Skip unknown vendors

    increase = ((today_cost - baseline) / baseline) * 100
    if increase >= 20:
        with log_file.open("a") as f:
            f.write(
                f"{timestamp} — ⚠️ {vendor} cost spike: ${today_cost:.2f} "
                f"(↑{increase:.1f}% over baseline ${baseline:.2f})\n"
            )

if __name__ == "__main__":
    # Example: Xfinity bill jumped to $102
    log_financial_risk("Xfinity", 102.00)
