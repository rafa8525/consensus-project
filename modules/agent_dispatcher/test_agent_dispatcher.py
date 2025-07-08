# test_agent_dispatcher.py
import unittest
from agent_dispatcher import dispatch_agent

class TestAgentDispatcher(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = [
            {"name": "Legal Advisor", "skills": ["contracts", "privacy"]},
            {"name": "Fitness Coach", "skills": ["bmi", "workouts"]},
            {"name": "Data Analyst", "skills": ["charts", "forecasting"]}
        ]

    def test_name_match(self):
        agent, reason = dispatch_agent("I need a Legal Advisor", self.manifest)
        self.assertEqual(agent, "Legal Advisor")
        self.assertIn("matched by name", reason)

    def test_skill_match(self):
        agent, reason = dispatch_agent("Can you help me with my BMI?", self.manifest)
        self.assertEqual(agent, "Fitness Coach")
        self.assertIn("matched by skill", reason)

    def test_no_match(self):
        agent, reason = dispatch_agent("I need help with guitar tuning.", self.manifest)
        self.assertIsNone(agent)
        self.assertEqual(reason, "no match")

if __name__ == '__main__':
    unittest.main()
