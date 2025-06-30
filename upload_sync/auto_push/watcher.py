import os
import shutil
import time
import subprocess

SOURCE_FOLDER = "C:\\Users\\rlymp\\Downloads"  # Or wherever AI saves temp files
TARGET_FOLDER = "C:\\Users\\rlymp\\consensus-project\\upload_sync\\auto_push"
GIT_PUSH_SCRIPT = "C:\\Users\\rlymp\\consensus-project\\upload_sync\\auto_push\\push_to_github.py"

def move_new_files():
    for filename in os.listdir(SOURCE_FOLDER):
        if filename.endswith(".md"):
            src_path = os.path.join(SOURCE_FOLDER, filename)
            dst_path = os.path.join(TARGET_FOLDER, filename)
            shutil.move(src_path, dst_path)
            print(f"✅ Moved {filename} to auto_push")
            subprocess.run(["python", GIT_PUSH_SCRIPT])

if __name__ == "__main__":
    print("👀 Watching for .md files to move...")
    while True:
        move_new_files()
        time.sleep(30)
