import logging
import time
import random

class Executor:
    def __init__(self):
        logging.info("[Executor] Initialized with enhanced logic")

    def execute(self, tasks):
        logging.info("[Executor] Executing enriched tasks with realism...")
        results = []
        for task in tasks:
            logging.info(f"[Executor] Running: {task}")
            # Simulated success or delay for realism
            time.sleep(random.uniform(0.1, 0.3))
            if "error" in task.lower():
                results.append(f"❌ {task} → failed")
                logging.warning(f"[Executor]⚠️ Task failed: {task}")
            else:
                results.append(f"✅ {task} → done")
        return results
