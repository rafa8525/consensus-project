import os
import time
import subprocess
from datetime import datetime
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
    memory_path = os.path.expanduser("~/consensus-project/memory/")

    # Embedded Python code to generate .flag file
    flag_command = (
        "import os; from datetime import datetime; "
        "timestamp = datetime.now().strftime('%Y-%m-%d_%H%M'); "
        "flag_path = os.path.expanduser(f'~/consensus-project/memory/logs/system/absorb_confirmation_{timestamp}.flag'); "
        "open(flag_path, 'w').close()"
    )

    # ✅ Corrected: using actual working scripts from /tools/
    absorb_cmd = (
        "/usr/bin/python3 ~/consensus-project/tools/absorb_runner.py && "
        "/usr/bin/python3 ~/consensus-project/tools/absorb_log_append.py auto && "
        f"/usr/bin/python3 -c \"{flag_command}\""
    )

    # Make sure logs/system directory exists
    os.makedirs(os.path.expanduser("~/consensus-project/memory/logs/system/"), exist_ok=True)

    event_handler = MemoryAbsorbHandler(absorb_cmd)
    observer = Observer()
    observer.schedule(event_handler, memory_path, recursive=True)
    observer.start()
    print(f"✅ [watchdog] Monitoring changes in: {memory_path}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 [watchdog] Stopped by user.")
        observer.stop()
    observer.join()
