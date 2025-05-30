import logging

class Planner:
    def __init__(self):
        logging.info("[Planner] Initialized with deeper task modeling")

    def plan(self, goal):
        logging.info(f"[Planner] Breaking down goal: {goal}")
        base_tasks = [
            f"Clarify objective of '{goal}'",
            f"Gather resources for '{goal}'",
            f"Define milestones for '{goal}'",
            f"Assign responsibilities for '{goal}'",
            f"Set timelines for '{goal}'",
            f"Execute initial steps of '{goal}'",
        ]
        logging.info(f"[Planner] Generated detailed plan: {base_tasks}")
        return base_tasks
