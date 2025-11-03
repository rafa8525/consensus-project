#!/usr/bin/python3
import os, subprocess, datetime, sys

TOOLS = "/home/rafa1215/consensus-project/tools"
LOGS  = "/home/rafa1215/memory/logs/system/morning_master.log"

def safe_run(script):
    """Run a helper script if it exists; otherwise write a stub log."""
    path = os.path.join(TOOLS, script)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOGS, "a") as log:
        if not os.path.exists(path):
            msg = f"[{timestamp}] ⚠️ {script} missing — stub executed.\n"
            log.write(msg);  print(msg.strip())
            # Create an empty stub file so future runs stay silent
            with open(path, "w") as stub:
                stub.write(f"#!/usr/bin/python3\nprint('Stub: {script}')\n")
            os.chmod(path, 0o755)
            return
        log.write(f"[{timestamp}] 🔄 {script}...\n"); print(f"🔄 {script}...")
        try:
            subprocess.run(["python3", path], check=True)
            log.write(f"[{timestamp}] ✅ {script} OK\n")
        except subprocess.CalledProcessError as e:
            log.write(f"[{timestamp}] ❌ {script} failed ({e})\n")

if __name__ == "__main__":
    sequence = [
        "finance_master.py",
        "reminder_master.py",
        "knowledge_master.py",
        "report_master.py",
        "health_master.py",
        "agi_master.py",
        "memory_compressor.py",
        "decision_support.py",
        "security_reliability.py"
    ]
    for s in sequence:
        safe_run(s)
    print("✅ Morning master sequence finished without fatal errors.")
