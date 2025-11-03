# consensus-project/tools/state_tracker.py
# Utility to persist and retrieve agent state

import json
import os
from datetime import datetime

STATE_DIR = os.path.expanduser("~/consensus-project/memory/logs/agents/state/")
os.makedirs(STATE_DIR, exist_ok=True)

def get_state_file(agent_name):
    return os.path.join(STATE_DIR, f"{agent_name}.json")

def load_agent_state(agent_name):
    path = get_state_file(agent_name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {
        "last_run": None,
        "last_status": "never_run",
        "last_result": None,
        "error": None
    }

def save_agent_state(agent_name, status, result=None, error=None):
    path = get_state_file(agent_name)
    state = {
        "last_run": datetime.now().isoformat(),
        "last_status": status,
        "last_result": result,
        "error": error
    }
    with open(path, "w") as f:
        json.dump(state, f, indent=2)

def was_recent_success(agent_name, minutes=60):
    from datetime import datetime, timedelta
    state = load_agent_state(agent_name)
    if state["last_status"] != "success" or not state["last_run"]:
        return False
    last_run = datetime.fromisoformat(state["last_run"])
    return datetime.now() - last_run < timedelta(minutes=minutes)

if __name__ == "__main__":
    # Example use:
    save_agent_state("gmail_agent", status="success", result="Inbox parsed")
    print(load_agent_state("gmail_agent"))
