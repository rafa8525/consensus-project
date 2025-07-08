# fitness_coach_agent.py
from datetime import datetime

mock_bmi_log = {"date": "2025-07-07", "value": 25.4}
mock_workout_log = {"date": "2025-07-06", "activity": "Pool laps", "count": 50}

def respond(user_input: str) -> str:
    response = ["👟 Fitness Coach Activated"]
    if "bmi" in user_input.lower():
        bmi = mock_bmi_log['value']
        status = "slightly high" if bmi > 24.9 else "within range"
        response.append(f"\n🧍 BMI Tracking:\n- Last BMI log: {bmi} ({mock_bmi_log['date']})\n- Status: {status}")
    if any(kw in user_input.lower() for kw in ["workout", "swim", "laps", "exercise"]):
        log = mock_workout_log
        response.append(f"\n💪 Workout Log:\n- Last: {log['activity']} ({log['count']}), {log['date']}\n- Suggestion: Add strength session this week")
    response.append("\n📲 Want me to log today’s BMI or workout?")
    return "\n".join(response)
