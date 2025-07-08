# agent_team_demo.py
from project_manager_agent import respond as pm_response
from data_analyst_agent import respond as analyst_response
from legal_advisor_agent import respond as legal_response

def simulate_collaboration():
    prompt = "Review project risk forecast for the upcoming API rollout and check if our licensing policy is valid."
    print("🔗 Multi-Agent Collaboration Triggered")
    print("\n🧠 Project Manager:")
    print(pm_response(prompt))

    print("\n📊 Data Analyst:")
    print(analyst_response(prompt))

    print("\n📜 Legal Advisor:")
    print(legal_response(prompt))

if __name__ == '__main__':
    simulate_collaboration()
