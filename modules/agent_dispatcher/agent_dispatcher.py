# agent_dispatcher.py
import json
import re
from fitness_coach_agent import respond as fitness_response
from project_manager_agent import respond as pm_response
from legal_advisor_agent import respond as legal_response
from data_analyst_agent import respond as analyst_response

def load_manifest(path='agents_manifest.json'):
    with open(path, 'r') as f:
        return json.load(f)

def dispatch_agent(user_input, manifest):
    input_cleaned = user_input.lower()
    for agent in manifest:
        if agent['name'].lower() in input_cleaned:
            return agent['name'], "matched by name"
        for skill in agent['skills']:
            if re.search(rf'\b{re.escape(skill.lower())}\b', input_cleaned):
                return agent['name'], f"matched by skill: {skill}"
    return None, "no match"

def route_to_agent(agent_name, user_input):
    if agent_name == "Fitness Coach":
        return fitness_response(user_input)
    elif agent_name == "Project Manager":
        return pm_response(user_input)
    elif agent_name == "Legal Advisor":
        return legal_response(user_input)
    elif agent_name == "Data Analyst":
        return analyst_response(user_input)
    return "⚠️ No live logic connected to this agent yet."

if __name__ == "__main__":
    manifest = load_manifest()
    while True:
        user_input = input("Enter a request: ")
        if user_input.strip().lower() in ['exit', 'quit']:
            break
        agent, reason = dispatch_agent(user_input, manifest)
        if agent:
            print(f"✅ Dispatching to: {agent} ({reason})")
            print(route_to_agent(agent, user_input))
        else:
            print("⚠️ No matching agent found.")
