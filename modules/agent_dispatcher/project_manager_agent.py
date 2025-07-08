# project_manager_agent.py
from datetime import datetime

tasks = [
    {"name": "Finalize VPN rollout", "due": "2025-07-06", "status": "complete"},
    {"name": "Connect BMI tracker to dispatcher", "due": "2025-07-07", "status": "complete"},
    {"name": "Hook up Project Manager agent", "due": "2025-07-08", "status": "in progress"},
    {"name": "GitHub auto-sync verification", "due": "2025-07-09", "status": "pending"}
]

def respond(user_input: str) -> str:
    today = datetime.today().strftime("%Y-%m-%d")
    overdue = [t for t in tasks if t['due'] < today and t['status'] != 'complete']
    upcoming = [t for t in tasks if t['due'] >= today and t['status'] != 'complete']

    response = ["🧠 Project Manager Activated"]
    if overdue:
        response.append("\n⚠️ Overdue Tasks:")
        for t in overdue:
            response.append(f"- {t['name']} (was due {t['due']})")
    else:
        response.append("\n✅ No overdue tasks.")
    if upcoming:
        response.append("\n📅 Upcoming Tasks:")
        for t in upcoming:
            response.append(f"- {t['name']} (due {t['due']})")
    return "\n".join(response)
