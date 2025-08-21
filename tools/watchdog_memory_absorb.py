import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MemoryAbsorbHandler(FileSystemEventHandler):
    def __init__(self, absorb_cmd):
        super().__init__()
        self.absorb_cmd = absorb_cmd

    def on_created(self, event):
        if not event.is_directory:
            print(f"[watchdog] File created: {event.src_path}")
            subprocess.Popen(self.absorb_cmd, shell=True)

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[watchdog] File modified: {event.src_path}")
            subprocess.Popen(self.absorb_cmd, shell=True)

if __name__ == "__main__":
    import os
    memory_path = os.path.expanduser("~/consensus-project/memory")
    absorb_cmd = "/usr/bin/python3 ~/consensus-project/tools/absorb_runner.py && /usr/bin/python3 ~/consensus-project/tools/absorb_log_append.py auto"

    event_handler = MemoryAbsorbHandler(absorb_cmd)
    observer = Observer()
    observer.schedule(event_handler, memory_path, recursive=True)
    observer.start()
    print(f"Watching '{memory_path}' for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
