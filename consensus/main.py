import argparse
import logging
import os
import sys

from agents.planner import Planner
from agents.researcher import Researcher
from agents.executor import Executor
from agents.memory_manager import MemoryManager

def run_cli():
    # Fix logging UnicodeEncodeError by ignoring problematic characters
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)

    parser = argparse.ArgumentParser(description="Run the Consensus agent simulation.")
    parser.add_argument("--goal", required=True, help="The goal for the agents to achieve")
    args = parser.parse_args()

    logging.info("Consensus CLI Agent simulation starting...\n")

    # Initialize agents
    planner = Planner()
    researcher = Researcher()
    executor = Executor()
    memory_manager = MemoryManager()

    # Step 1: Planner creates a task plan
    logging.info(f"[Planner] Received goal: {args.goal}")
    task_plan = planner.create_plan(args.goal)
    logging.info(f"[Planner] Generated task plan: {task_plan}")

    # Step 2: Researcher enriches the task plan
    enriched_plan = researcher.enrich_plan(task_plan)
    logging.info(f"[Researcher] Enriched tasks: {enriched_plan}")

    # Step 3: Executor runs the enriched tasks
    execution_log = executor.execute(enriched_plan)
    for line in execution_log:
        logging.info(line)

    # Step 4: MemoryManager stores the results
    memory_manager.store(execution_log)
    logging.info(f"[MemoryManager] Memory log updated: {execution_log}")

    logging.info("Full agent simulation complete.")

if __name__ == "__main__":
    run_cli()
