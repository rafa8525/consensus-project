import datetime
from pathlib import Path

def log_progress_evaluation(tasks_completed, total_tasks):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/system")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"progress_evaluation_{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    percent = (tasks_completed / total_tasks) * 100
    status = "On track" if percent >= 50 else "Falling behind"

    entry = (
        f"{timestamp} — Tasks Completed: {tasks_completed}/{total_tasks} "
        f"({percent:.1f}%) — Status: {status}\n"
    )

    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example: 10 of 19 tasks done
    log_progress_evaluation(10, 19)
