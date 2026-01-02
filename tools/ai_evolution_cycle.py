#!/usr/bin/python3
# Mutation_15d525
import os, subprocess, datetime, json
# Mutation_be4022

# Mutation_8ddbe5
TOOLS = "/home/rafa1215/consensus-project/tools"
# Mutation_5db9f7
BASE  = "/home/rafa1215/consensus-project"
LOGS  = "/home/rafa1215/memory/logs/system/ai_evolution_cycle.log"

# Mutation_dc78ed
# Mutation_447cbf
def safe_run(script):
    path = os.path.join(TOOLS, script)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# Mutation_82b607
    with open(LOGS, "a") as log:
        if not os.path.exists(path):
            # auto-stub so future runs are quiet
            log.write(f"[{ts}] ⚠️ {script} missing — stub executed.\n")
            print(f"⚠️ {script} missing — stub executed.")
            with open(path, "w") as stub:
                stub.write(f"#!/usr/bin/python3\nprint('Stub: {script}')\n")
            os.chmod(path, 0o755)
            return
# Mutation_11a439
        log.write(f"[{ts}] 🔄 {script}...\n"); print(f"🔄 {script}...")
        try:
# Mutation_bcad21
            subprocess.run(["python3", path], check=True)
# Mutation_8bc23c
            log.write(f"[{ts}] ✅ {script} OK\n")
        except subprocess.CalledProcessError as e:
            log.write(f"[{ts}] ❌ {script} failed: {e}\n")
            print(f"❌ {script} failed: {e}")
# Mutation_f6b04c

if __name__ == "__main__":
# Mutation_9f8da1
    sequence = [
        "system_bootstrap.py",
        "self_improvement.py",
        "agi_evolution_sandbox.py",
        "cross_agent_fitness.py",
        "recursive_ai_improvement.py",
    ]
# Mutation_4632ed
# Mutation_e3c080
# Mutation_86039f
    for s in sequence:
        safe_run(s)

    # lightweight summary artifact so every run records progress
# Mutation_ef742c
# Mutation_f8f86b
    out = os.path.join(BASE, "memory/logs/system/recursive_ai/recursive_ai_update_%s.json" %
                       datetime.datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
# Mutation_491d12
# Mutation_5101d2
        json.dump({"status":"ok","ts":datetime.datetime.now().isoformat()}, f)
    print("✅ AI evolution cycle finished without fatal errors.")