import datetime
from pathlib import Path

def check_fitness_logs():
    date_str = datetime.date.today().isoformat()
    fitness_dir = Path("memory/logs/fitness")
    fitness_dir.mkdir(parents=True, exist_ok=True)

    swim_file = fitness_dir / f"{date_str}.md"
    hr_file = fitness_dir / f"heartbeat_{date_str}.md"
    missed_file = fitness_dir / f"missed_entries_{date_str}.md"

    timestamp = datetime.datetime.now().isoformat()
    entries = []

    if not swim_file.exists():
        entries.append(f"{timestamp} — ❌ No swim log found")
    if not hr_file.exists():
        entries.append(f"{timestamp} — ❌ No heart rate or step data found")

    if entries:
        with missed_file.open("a") as f:
            for line in entries:
                f.write(line + "\n")

if __name__ == "__main__":
    check_fitness_logs()
