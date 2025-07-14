import datetime
from pathlib import Path

def log_agent_lesson(agent_name, lesson):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/agents")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"lessons_learned_{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    entry = f"{timestamp} — Agent: {agent_name} — Lesson: {lesson}\n"
    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example entry
    log_agent_lesson("Scheduler", "Avoid triggering reminders before geofence exits.")
