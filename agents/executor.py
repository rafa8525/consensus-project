# agents/executor.py

class Executor:
    def __init__(self):
        self.execution_log = []

    def execute(self, enriched_tasks):
        print(f"[Executor] Executing tasks...")
        for task in enriched_tasks:
            result = f"✅ {task} → done"
            self.execution_log.append(result)
            print(result)
        return self.execution_log
