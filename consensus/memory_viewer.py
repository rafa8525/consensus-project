import argparse
import os

MEMORY_DIR = os.path.join(os.path.dirname(__file__), '..', 'memory')

def list_memory_files():
    files = os.listdir(MEMORY_DIR)
    print("📂 Memory Files:")
    for f in files:
        print("•", f)

def view_memory_file(filename):
    path = os.path.join(MEMORY_DIR, filename)
    if not os.path.exists(path):
        print(f"🚫 File '{filename}' not found.")
        return
    with open(path, 'r', encoding='utf-8') as file:
        print(f"📄 Contents of '{filename}':")
        print(file.read())

def search_memory(keyword):
    print(f"🔍 Searching for keyword: '{keyword}'\n")
    found = False
    for file in os.listdir(MEMORY_DIR):
        path = os.path.join(MEMORY_DIR, file)
        if not os.path.isfile(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            matches = [line.strip() for line in lines if keyword.lower() in line.lower()]
            if matches:
                found = True
                print(f"\n📁 {file}:")
                for match in matches:
                    print("•", match)
    if not found:
        print("🚫 No matches found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true', help='List all memory logs')
    parser.add_argument('--view', type=str, help='View a specific memory log')
    parser.add_argument('--search', type=str, help='Search all logs for a keyword')
    args = parser.parse_args()

    if args.list:
        list_memory_files()
    elif args.view:
        view_memory_file(args.view)
    elif args.search:
        search_memory(args.search)
    else:
        parser.print_help()
