import time
from datetime import datetime

# List your 55 agent names (IDs or process names)
AGENT_LIST = [f"Agent_{i:02}" for i in range(1, 56)]  # e.g. Agent_01 to Agent_55

# Path to the heartbeat log file
HEARTBEAT_LOG = "memory/logs/agent_heartbeat_log.md"

def ping_agent(agent_name):
    # Placeholder logic. Replace with actual ping/call if agents are real services.
    # Return True if alive, False if down
    return True  # Simulate all alive for now

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    results = []
    for agent in AGENT_LIST:
        alive = ping_agent(agent)
        status = "ALIVE" if alive else "UNRESPONSIVE"
        results.append(f"[{now}] {agent}: {status}")
    # Append to log
    with open(HEARTBEAT_LOG, "a") as log:
        log.write("\n" + "\n".join(results))
    print(f"Heartbeat check completed at {now}. Results logged.")

if __name__ == "__main__":
    main()
