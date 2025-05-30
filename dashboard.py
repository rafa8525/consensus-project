import os
import datetime

LOGS_FOLDER = "logs"

def list_logs():
    print("\n📂 Available Log Files:")
    files = sorted(
        [f for f in os.listdir(LOGS_FOLDER) if f.endswith(".txt")],
        reverse=True
    )
    for idx, fname in enumerate(files):
        print(f"{idx+1}. {fname}")
    return files

def view_log(filepath):
    print(f"\n📄 Contents of {filepath}:\n{'-'*50}")
    with open(filepath, "r", encoding="utf-8") as f:
        print(f.read())

def main():
    print("🧠 Consensus Agent Run Dashboard\n")
    if not os.path.exists(LOGS_FOLDER):
        print(f"❌ Log folder '{LOGS_FOLDER}' not found.")
        return

    files = list_logs()
    if not files:
        print("No logs found.")
        return

    while True:
        choice = input("\nEnter the number of the log to view (or Q to quit): ").strip()
        if choice.lower() == 'q':
            break
        if not choice.isdigit() or not (1 <= int(choice) <= len(files)):
            print("Invalid selection.")
            continue
        selected = files[int(choice)-1]
        view_log(os.path.join(LOGS_FOLDER, selected))

if __name__ == "__main__":
    main()
