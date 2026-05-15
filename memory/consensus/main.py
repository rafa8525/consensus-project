import argparse
import logging
from agents.planner import Planner
from agents.researcher import Researcher
from agents.executor import Executor
from agents.memory_manager import MemoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("consensus_log.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def run_cli(goal):
    logging.info("Consensus CLI Agent simulation starting...")
    print("\n🧠 Consensus CLI Agent simulation starting...\n")

    # Initialize agents
    planner = Planner()
    researcher = Researcher()
    executor = Executor()
    memory_manager = MemoryManager()

    # Planning
    logging.info(f"[Planner] Received goal: {goal}")
    print(f"[Planner] Received goal: {goal}")
    task_plan = planner.generate_plan(goal)
    logging.info(f"[Planner] Generated task plan: {task_plan}")
    print(f"[Planner] Generated task plan: {task_plan}")

    # Researching
    enriched_tasks = researcher.enrich(task_plan)
    logging.info(f"[Researcher] Enriched tasks: {enriched_tasks}")
    print(f"[Researcher] Enriched tasks: {enriched_tasks}")

    # Executing
    print("[Executor] Executing tasks...")
    execution_log = []
    for task in enriched_tasks:
        result = executor.execute(task)
        print(result)
        logging.info(result)
        execution_log.append(result)

    # Memory management
    print("[MemoryManager] Archiving results...")
    memory_manager.store(execution_log)

    print("\n✅ Full agent simulation complete.\n")
    logging.info("Full agent simulation complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Consensus CLI Agent.")
    parser.add_argument("--goal", type=str, required=True, help="The goal to simulate")
    args = parser.parse_args()
    run_cli(args.goal)
