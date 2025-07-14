import datetime
from pathlib import Path

def log_steps_hr(step_count, heart_rate):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/fitness")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"heartbeat_{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    entry = f"{timestamp} — Steps: {step_count} — Avg HR: {heart_rate}\n"
    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example usage: 8200 steps, 104 bpm
    log_steps_hr(8200, 104)
