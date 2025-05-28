# agents/memory_manager.py

class MemoryManager:
    def __init__(self):
        self.memory_log = []

    def store(self, execution_log):
        print(f"[MemoryManager] Archiving results...")
        self.memory_log.extend(execution_log)
        print(f"[MemoryManager] Memory log updated: {self.memory_log}")
        return True
