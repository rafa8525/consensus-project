# agents/researcher.py

class Researcher:
    def __init__(self):
        self.enriched_tasks = []

    def enrich_plan(self, task_list):
        print(f"[Researcher] Analyzing tasks: {task_list}")
        self.enriched_tasks = [task + " [context added]" for task in task_list]
        print(f"[Researcher] Enriched tasks: {self.enriched_tasks}")
        return self.enriched_tasks
