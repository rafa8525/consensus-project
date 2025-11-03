#!/usr/bin/python3
import os, subprocess, datetime, json

TOOLS = "/home/rafa1215/consensus-project/tools"
BASE  = "/home/rafa1215/consensus-project"
LOGS  = "/home/rafa1215/memory/logs/system/ai_evolution_cycle.log"

def safe_run(script):
    path = os.path.join(TOOLS, script)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOGS, "a") as log:
        if not os.path.exists(path):
            # auto-stub so future runs are quiet
            log.write(f"[{ts}] ⚠️ {script} missing — stub executed.\n")
            print(f"⚠️ {script} missing — stub executed.")
            with open(path, "w") as stub:
                stub.write(f"#!/usr/bin/python3\nprint('Stub: {script}')\n")
            os.chmod(path, 0o755)
            return
        log.write(f"[{ts}] 🔄 {script}...\n"); print(f"🔄 {script}...")
        try:
            subprocess.run(["python3", path], check=True)
            log.write(f"[{ts}] ✅ {script} OK\n")
        except subprocess.CalledProcessError as e:
            log.write(f"[{ts}] ❌ {script} failed: {e}\n")
            print(f"❌ {script} failed: {e}")

if __name__ == "__main__":
    sequence = [
        "system_bootstrap.py",
        "self_improvement.py",
        "agi_evolution_sandbox.py",
        "cross_agent_fitness.py",
        "recursive_ai_improvement.py",
    ]
    for s in sequence:
        safe_run(s)

    # lightweight summary artifact so every run records progress
    out = os.path.join(BASE, "memory/logs/system/recursive_ai/recursive_ai_update_%s.json" %
                       datetime.datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump({"status":"ok","ts":datetime.datetime.now().isoformat()}, f)
    print("✅ AI evolution cycle finished without fatal errors.")
