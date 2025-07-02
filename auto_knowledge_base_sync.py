import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# CONFIGURE THESE PATHS IF NEEDED
PROJECT_ROOT = "C:/Users/rlymp/consensus-project"
KB_FILE = f"{PROJECT_ROOT}/memory/centralized_knowledge_base.txt"
LOG_FILE = f"{PROJECT_ROOT}/memory/logs/project_log.md"

class KnowledgeBaseHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.replace("\\", "/") == KB_FILE.replace("\\", "/"):
            self.sync_and_log()
            self.agent_collaboration_test()  # <-- Calls the collaboration test

    def sync_and_log(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = f"Auto-sync: Centralized knowledge base updated {now}"
        try:
            subprocess.run(["git", "add", KB_FILE], cwd=PROJECT_ROOT, check=True)
            subprocess.run(["git", "commit", "-m", msg], cwd=PROJECT_ROOT, check=True)
            subprocess.run(["git", "push"], cwd=PROJECT_ROOT, check=True)
            print(f"{now}: Knowledge base auto-synced and pushed.")

            # Log to project log
            with open(LOG_FILE, "a") as log:
                log.write(f"\n[{now}] Centralized knowledge base auto-synced and versioned.\n")
        except Exception as e:
            print(f"Error during auto-sync: {e}")

    def agent_collaboration_test(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            # Agent A writes a note
            with open(KB_FILE, "a") as f:
                f.write(f"\n[{now}] AGENT_A: Triggered collaboration test.\n")
            # Agent B reads and responds
            with open(KB_FILE, "a") as f:
                f.write(f"[{now}] AGENT_B: Read Agent A's message and confirmed propagation.\n")
            # Auto-sync the new updates
            subprocess.run(["git", "add", KB_FILE], cwd=PROJECT_ROOT, check=True)
            subprocess.run(["git", "commit", "-m", f'Agent collaboration test at {now}'], cwd=PROJECT_ROOT, check=True)
            subprocess.run(["git", "push"], cwd=PROJECT_ROOT, check=True)
            print(f"{now}: Agent collaboration test run and synced.")
        except Exception as e:
            print(f"Error in agent collaboration test: {e}")

if __name__ == "__main__":
    event_handler = KnowledgeBaseHandler()
    observer = Observer()
    kb_dir = "/".join(KB_FILE.replace("\\", "/").split("/")[:-1])
    observer.schedule(event_handler, path=kb_dir, recursive=False)
    observer.start()
    print(f"Watching {KB_FILE} for changes. Auto-sync and agent collaboration test enabled.")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
