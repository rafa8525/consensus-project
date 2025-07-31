#!/usr/bin/env python3
import os
import time
from datetime import datetime

# Path to memory folder
MEMORY_FOLDER = "/home/rafa1215/consensus-project/memory/"
# Path to heartbeat log
LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/system/memory_folder_heartbeat.log"

def deep_scan_memory():
    file_count = 0
    last_modified = None
    latest_file = None

    for root, dirs, files in os.walk(MEMORY_FOLDER):
        for name in files:
            file_count += 1
            path = os.path.join(root, name)
            mtime = os.path.getmtime(path)
            if last_modified is None or mtime > last_modified:
                last_modified = mtime
                latest_file = path

    last_modified_str = datetime.fromtimestamp(last_modified).strftime("%Y-%m-%d %H:%M:%S") if last_modified else "N/A"

    # Write log
    with open(LOG_FILE, "a") as log:
        log.write(f"[{datetime.now()}] Memory folder scan complete.\n")
        log.write(f"Total files: {file_count}\n")
        log.write(f"Last modified file: {latest_file}\n")
        log.write(f"Last modified time: {last_modified_str}\n")
        log.write("----\n")

    print(f"[{datetime.now()}] Deep scan complete: {file_count} files found. Latest file: {latest_file}")

if __name__ == "__main__":
    deep_scan_memory()
