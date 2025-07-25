import os
from datetime import date
from pathlib import Path

today = date.today().strftime("%Y-%m-%d")
log_dir = Path("/home/rafa1215/consensus-project/memory/logs/nutrition")
log_file = log_dir / f"{today}_nutrition_log.md"
fallback_log = log_dir / "meal_log.md"

# Check if barcode-based meal log exists
if not log_file.exists():
    with fallback_log.open("a") as f:
        f.write(f"\n⚠️ No barcode meals auto-logged for {today}. Prompted user manually.\n")

    # Trigger SMS (simplified stub)
    from send_reminder import send_sms_reminder
    send_sms_reminder("No meals were auto-logged today. Please scan a barcode or log manually.")

# Log to agent activity
agent_log_dir = Path("/home/rafa1215/consensus-project/memory/logs/agents")
agent_log = agent_log_dir / f"heartbeat_{today}.md"
agent_log_dir.mkdir(parents=True, exist_ok=True)

entry = f"NutritionFallbackAgent: {'Log verified, no action needed.' if log_file.exists() else 'No log found — fallback triggered.'}"
with agent_log.open("a") as f:
    f.write(f"\n{entry}\n")
