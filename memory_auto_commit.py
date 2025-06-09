import subprocess
import datetime
import os

TRACKED_FOLDERS = ["memory", "calendar"]
COMMIT_MSG = f"Auto-sync memory/calendar: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

def run_git_command(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("❌ Git Error:", result.stderr.strip())
        return False
    return True

def has_changes():
    for folder in TRACKED_FOLDERS:
        result = subprocess.run(["git", "status", "--porcelain", folder], stdout=subprocess.PIPE, text=True)
        if result.stdout.strip():
            return True
    return False

def commit_and_push():
    print("📦 Checking for memory/calendar changes...")
    if not has_changes():
        print("⚠️ No updates to push.")
        return

    print("📝 Committing changes...")
    for folder in TRACKED_FOLDERS:
        run_git_command(["git", "add", folder])

    if not run_git_command(["git", "commit", "-m", COMMIT_MSG]):
        return

    print("🚀 Pushing to GitHub...")
    if not run_git_command(["git", "push"]):
        return

    print("✅ Auto-sync complete.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    commit_and_push()
