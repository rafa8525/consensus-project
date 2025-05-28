# scripts/main.py

from agents.planner import Planner
from agents.researcher import Researcher
from agents.executor import Executor

def start_simulation():
    print("🧠 Consensus Project: Agent simulation starting...")

    # Initialize agents
    planner = Planner()
    researcher = Researcher()
    executor = Executor()

    # Step 1: Planner creates a task plan
    goal = "organize team meeting"
    task_plan = planner.create_plan(goal)

    # Step 2: Researcher enriches the task plan
    enriched_plan = researcher.enrich_plan(task_plan)

    # Step 3: Executor runs the enriched tasks
    execution_log = executor.execute(enriched_plan)

    print("\n✅ Simulation complete.")

if __name__ == "__main__":
    start_simulation()
