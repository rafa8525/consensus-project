import datetime
from pathlib import Path

def log_agent_insight(agent_name, insight):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/agents")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"knowledge_shared_{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    entry = f"{timestamp} — Agent: {agent_name} — Insight: {insight}\n"
    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example: agent MemoryManager logs an insight
    log_agent_insight("MemoryManager", "Linked swimming behavior to BMI reduction")
