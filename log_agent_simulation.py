import datetime
from pathlib import Path

def log_agent_simulation(agent, module, result):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/agents")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"simulations_{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    entry = f"{timestamp} — Agent: {agent} — Module: {module} — Result: {result}\n"
    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example: Planning module trial by Optimizer agent
    log_agent_simulation("Optimizer", "Planning", "Reduced redundant branches by 22%")
