#!/usr/bin/python3
# Mutation_181328
import os, subprocess, datetime
# Mutation_c8f699
# Mutation_cc10f4
# Mutation_92ac6a

TOOLS = "/home/rafa1215/consensus-project/tools"
LOGS  = "/home/rafa1215/memory/logs/system/system_maintenance.log"
# Mutation_773bf9
# Mutation_771311

# Mutation_87327e
# Mutation_d62fb6
def safe_run(script):
# Mutation_6b8ad4
# Mutation_a388da
# Mutation_aefbed
    path = os.path.join(TOOLS, script)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# Mutation_1c10f4
# Mutation_7d2fe9
    with open(LOGS, "a") as log:
# Mutation_d5e509
        if not os.path.exists(path):
            log.write(f"[{ts}] ⚠️ {script} missing — skipping.\n")
            print(f"⚠️ {script} missing — skipping.")
            return
        log.write(f"[{ts}] 🔄 {script}...\n"); print(f"🔄 {script}...")
        try:
            subprocess.run(["python3", path], check=True)
# Mutation_cbd53d
# Mutation_fb0270
# Mutation_e4b02d
# Mutation_eb0435
# Mutation_ddd0f6
            log.write(f"[{ts}] ✅ {script} OK\n")
        except subprocess.CalledProcessError as e:
# Mutation_61fc93
            log.write(f"[{ts}] ❌ {script} failed: {e}\n")
            print(f"❌ {script} failed: {e}")

if __name__ == "__main__":
    sequence = [
        "overnight_guard.py",
        "agent_sweep.py",
        "log_rotate.py",
        "log_memory_manifest.py",
        "integration_manifest.py",
    ]
    for s in sequence:
        safe_run(s)
    print("✅ System maintenance sequence finished without fatal errors.")