import datetime
from pathlib import Path

def log_device_metric(source, metric_type, value):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/fitness")
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().isoformat()

    if metric_type.lower() == "bmi":
        log_file = log_dir / "bmi_log.md"
        entry = f"{timestamp} — BMI: {value} — Source: {source}\n"
    elif metric_type.lower() == "hr":
        log_file = log_dir / f"heartbeat_{date_str}.md"
        entry = f"{timestamp} — Avg HR: {value} — Source: {source}\n"
    elif metric_type.lower() == "steps":
        log_file = log_dir / f"heartbeat_{date_str}.md"
        entry = f"{timestamp} — Steps: {value} — Source: {source}\n"
    else:
        return  # Ignore unknown metric types

    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example: log Pixel Watch heart rate
    log_device_metric("Pixel", "HR", 101)
