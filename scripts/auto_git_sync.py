import os
import subprocess
from datetime import datetime

os.chdir("/home/rafa1215/consensus-project")

# Stage all .md files under memory/logs recursively
subprocess.run("git add memory/logs/**/*.md", shell=True)

# Check if anything is staged
result = subprocess.run("git diff --cached --quiet", shell=True)
if result.returncode != 0:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subprocess.run(f'git commit -m "🧠 Auto-log sync for {timestamp}"', shell=True)
    subprocess.run("git push origin v1.1-dev", shell=True)
else:
    print("No changes to commit.")
