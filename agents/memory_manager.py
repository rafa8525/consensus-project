import os
from datetime import datetime

# Directory where memory logs will be stored
MEMORY_DIR = os.path.join("memory")

# You can toggle between "standard" and "minimal"
MEMORY_MODE = "minimal"

if not os.path.exists(MEMORY_DIR):
    os.makedirs(MEMORY_DIR)

class MemoryManager:
    def __init__(self):
        pass

    def store(self, entries):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"memory_log_{timestamp}.txt"
        filepath = os.path.join(MEMORY_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            for entry in entries:
                if MEMORY_MODE == "minimal":
                    clean_entry = entry.replace("✅", "").split("[")[0].strip()
                    file.write(clean_entry + "\n")
                else:
                    file.write(entry + "\n")

        print(f"[MemoryManager] Memory log written to: {filepath}")
        print(f"[MemoryManager] Memory log updated: {entries}")
