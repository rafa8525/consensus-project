# consensus/menu.py

from consensus import main
from consensus import memory_viewer
from consensus import scheduler

def main_menu():
    print("\n=== AI Consensus System Menu ===")
    print("1. Run Main Agent")
    print("2. View Memory Logs")
    print("3. Run Scheduled Goal")
    print("4. Exit")
    return input("Select an option: ")

if __name__ == "__main__":
    while True:
        choice = main_menu()
        if choice == "1":
            main.run()
        elif choice == "2":
            memory_viewer.view_logs()
        elif choice == "3":
            scheduler.run_scheduled_task()
        elif choice == "4":
            print("Exiting system.")
            break
        else:
            print("Invalid selection. Try again.")
