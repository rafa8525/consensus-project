import subprocess
import os

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def run_consensus():
    goal = input("Enter your goal: ").strip()
    subprocess.run(["python", "consensus/main.py", "--goal", goal])

def view_logs():
    subprocess.run(["python", "consensus/dashboard.py"])

def view_memory():
    subprocess.run(["python", "consensus/memory_viewer.py", "--list"])
    filename = input("Enter memory filename to view or 'search <term>': ").strip()
    if filename.startswith("search "):
        keyword = filename[len("search "):]
        subprocess.run(["python", "consensus/memory_viewer.py", "--search", keyword])
    else:
        subprocess.run(["python", "consensus/memory_viewer.py", "--view", filename])

def main_menu():
    while True:
        clear_screen()
        print("🧭 Consensus CLI Menu\n")
        print("1. Run Consensus Agent")
        print("2. View Logs")
        print("3. View or Search Memory")
        print("4. Exit")

        choice = input("\nSelect an option (1-4): ").strip()

        if choice == "1":
            run_consensus()
        elif choice == "2":
            view_logs()
        elif choice == "3":
            view_memory()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            input("Invalid choice. Press Enter to try again.")

if __name__ == "__main__":
    main_menu()
