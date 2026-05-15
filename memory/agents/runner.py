# Agent runner - simulate agent run and log to all systems
from datetime import datetime
from pathlib import Path

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

log_file = Path(f"logs/consensus_log_{timestamp}.txt")
memory_file = Path(f"memory/memory_log_{timestamp}.txt")
digest_file = Path("logs/daily_digest.txt")
goal_file = Path("scheduled_goal.txt")

goal = goal_file.read_text(encoding="utf-8").strip() if goal_file.exists() else "No goal set."
log_lines = [
    f"[{timestamp}] GOAL: {goal}",
    f"[{timestamp}] planner ran 3 tasks",
    f"[{timestamp}] executor confirmed 2 outputs",
    f"[{timestamp}] researcher fetched 1 summary"
]

Path("logs").mkdir(exist_ok=True)
log_file.write_text("\n".join(log_lines), encoding="utf-8")

Path("memory").mkdir(exist_ok=True)
memory_file.write_text("\n".join(log_lines), encoding="utf-8")

digest_content = f"""🧠 AI Consensus Digest - {datetime.now().strftime('%Y-%m-%d')}
===============================
• planner ran 3 tasks
• executor confirmed 2 outputs
• researcher fetched 1 summary
"""

digest_file.write_text(digest_content, encoding="utf-8")

print("✅ Agent run complete. Logs written:")
print(" -", log_file)
print(" -", memory_file)
print(" -", digest_file)
