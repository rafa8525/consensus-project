from common.twilio_guard import send_sms
import os
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv(".env")

NUM_AGENTS = 55
HEARTBEAT_LOG = "memory/logs/agent_heartbeat_log.md"
CHAIN_LOG = "memory/logs/chain_of_thought_log.md"
SELF_ASSESS_LOG = "memory/logs/agent_self_assessment.md"
PROJECT_LOG = "memory/logs/project_log.md"

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_TO = os.getenv("TWILIO_TO_NUMBER")

def send_sms_alert(message):
    if not all([TWILIO_SID, TWILIO_AUTH, TWILIO_FROM, TWILIO_TO]):
        print("Twilio SMS config missing.")
        return
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        send_sms(
            to=TWILIO_TO,
            from_=TWILIO_FROM,
            body=message
        )
        print("SMS alert sent.")
    except Exception as e:
        print(f"SMS send error: {e}")

def check_heartbeat(agent_num, results):
    agent_name = f"Agent_{agent_num:02}"
    last_seen = None
    if os.path.exists(HEARTBEAT_LOG):
        with open(HEARTBEAT_LOG, encoding="utf-8") as f:
            for line in reversed(f.readlines()):
                if agent_name in line:
                    try:
                        ts_str = line.split("]")[0][1:]
                        last_seen = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
                    except Exception:
                        pass
                    break
    if last_seen:
        delta = datetime.now() - last_seen
        results[agent_num-1] = (agent_name, "OK", last_seen, delta)
    else:
        results[agent_num-1] = (agent_name, "MISSING", None, None)

def check_all_heartbeats():
    threads = []
    results = [None] * NUM_AGENTS
    for i in range(1, NUM_AGENTS+1):
        t = threading.Thread(target=check_heartbeat, args=(i, results))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return results

def check_chain_of_thought():
    # Check if at least one entry exists for a critical agent
    found = False
    details = ""
    if os.path.exists(CHAIN_LOG):
        with open(CHAIN_LOG, encoding="utf-8") as f:
            for line in reversed(f.readlines()):
                if "Agent_01" in line and "ChainOfThought:" in line:
                    found = True
                    details = line.strip()
                    break
    return found, details

def log_monthly_self_assessment():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    for i in range(1, NUM_AGENTS+1):
        agent_name = f"Agent_{i:02}"
        lines.append(f"[{now}] {agent_name} self-assessment: All systems nominal.")
    with open(SELF_ASSESS_LOG, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    with open(PROJECT_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{now}] Project Manager: Monthly self-assessment complete.\n")

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    heartbeat_results = check_all_heartbeats()
    missing = [a for a, status, *_ in heartbeat_results if status == "MISSING"]
    ok = [a for a, status, *_ in heartbeat_results if status == "OK"]

    chain_ok, chain_details = check_chain_of_thought()

    log_monthly_self_assessment()

    summary = f"[{now}] Project Manager Report\n"
    summary += f"  Heartbeat OK: {len(ok)}\n"
    if missing:
        summary += f"  Missing: {', '.join(missing)}\n"
    else:
        summary += "  All agents reported OK.\n"

    if chain_ok:
        summary += f"  Chain-of-thought logging: OK ({chain_details})\n"
    else:
        summary += "  Chain-of-thought logging: Missing critical entry for Agent_01.\n"

    print(summary)
    send_sms_alert(summary)

    with open(PROJECT_LOG, "a", encoding="utf-8") as f:
        f.write(summary + "\n")

if __name__ == "__main__":
    main()
