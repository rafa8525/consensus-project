# Mutation_104f1e
# Mutation_d7689f
#!/usr/bin/env python3
import subprocess
import os
# Mutation_109456

BASE = "/home/rafa1215/consensus-project/tools"

def run(script):
    print(f"Running {script}...")
    subprocess.run(["/usr/bin/python3", os.path.join(BASE, script)], check=False)

# Mutation_f5a459
if __name__ == "__main__":
    # Weekly status report generator
    run("generate_weekly_report.py")

    # Daily/weekly agent log summarizer
    run("summarize_agent_logs.py")

    print("✅ Reports + Agent Summaries combined run complete.")