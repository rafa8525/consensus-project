# tests/test_pipeline.py

import unittest
from agents.planner import Planner
from agents.researcher import Researcher
from agents.executor import Executor
from agents.memory_manager import MemoryManager

class TestAgentPipeline(unittest.TestCase):
    def test_full_pipeline(self):
        planner = Planner()
        researcher = Researcher()
        executor = Executor()
        memory_manager = MemoryManager()

        # Simulate one full cycle
        goal = "test goal"
        plan = planner.create_plan(goal)
        enriched = researcher.enrich_plan(plan)
        results = executor.execute(enriched)
        memory_store_success = memory_manager.store(results)

        # Assertions
        self.assertTrue(len(plan) > 0)
        self.assertTrue(len(enriched) == len(plan))
        self.assertTrue(len(results) == len(plan))
        self.assertTrue(memory_store_success)
        self.assertTrue(len(memory_manager.memory_log) == len(plan))

if __name__ == "__main__":
    unittest.main()
