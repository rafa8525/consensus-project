# scripts/main.py

from agents.planner import Planner

def start_simulation():
    print("🧠 Consensus Project: Agent simulation starting...")

    # Initialize Planner agent
    planner = Planner()
    goal = "organize team meeting"
    task_plan = planner.create_plan(goal)

    # Simulate passing to next agent (placeholder)
    print(f"\nPassing plan to next agent: {task_plan}")

    print("\n✅ Simulation complete.")

if __name__ == "__main__":
    start_simulation()
