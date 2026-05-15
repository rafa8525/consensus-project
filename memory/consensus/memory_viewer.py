# consensus/memory_viewer.py

import os

def view_logs():
    memory_dir = "memory"
    logs = sorted([f for f in os.listdir(memory_dir) if f.endswith(".txt")])
    
    if not logs:
        print("No memory logs found.")
        return

    for i, file in enumerate(logs):
        print(f"{i+1}. {file}")
    
    choice = input("Select a file number to view or type a keyword to search: ").strip()
    
    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(logs):
            path = os.path.join(memory_dir, logs[index])
            with open(path, "r") as f:
                print(f.read())
        else:
            print("Invalid file number.")
    else:
        keyword = choice.lower()
        print(f"\nSearching memory logs for: '{keyword}'\n")
        for log_file in logs:
            path = os.path.join(memory_dir, log_file)
            with open(path, "r") as f:
                content = f.read()
                if keyword in content.lower():
                    print(f"\n--- {log_file} ---\n")
                    print(content)
