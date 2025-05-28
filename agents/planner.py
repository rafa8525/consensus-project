# agents/planner.py

class Planner:
    def __init__(self):
        self.tasks = []

    def create_plan(self, goal):
        print(f"[Planner] Received goal: {goal}")
        self.tasks = [f"Step 1 for {goal}", f"Step 2 for {goal}"]
        print(f"[Planner] Generated task plan: {self.tasks}")
        return self.tasks
