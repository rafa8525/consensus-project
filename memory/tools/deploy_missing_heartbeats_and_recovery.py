#!/usr/bin/env python3
import os
import stat
import textwrap

TOOLS_DIR = "/home/rafa1215/consensus-project/memory/tools"

# === Heartbeat script generator ===
def make_heartbeat_script(log_filename, message):
    return textwrap.dedent(f"""\
        #!/usr/bin/env python3
        import datetime
        import os

        LOG_DIR = "/home/rafa1215/consensus-project/memory/logs/system"
        os.makedirs(LOG_DIR, exist_ok=True)

        log_path = os.path.join(LOG_DIR, "{log_filename}")
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

        with open(log_path, "a") as f:
            f.write(f"{{timestamp}} {message}\\n")

        print(f"{{timestamp}} {message}")
    """)

# === Skipped task recovery ===
skipped_task_recovery = textwrap.dedent("""\
    #!/usr/bin/env python3
    import os
    import time
    import datetime
    import subprocess

    LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/system/skipped_task_recovery.log"

    TASKS = [
        ("VPN Test", "/home/rafa1215/consensus-project/memory/tools/log_vpn_heartbeat.py"),
        ("GitHub Sync", "/home/rafa1215/consensus-project/memory/tools/log_github_heartbeat.py"),
        ("Fitness Log", "/home/rafa1215/consensus-project/memory/tools/log_fitness_heartbeat.py"),
    ]

    def log(msg):
        ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        with open(LOG_FILE, "a") as f:
            f.write(f"{ts} {msg}\\n")
        print(f"{ts} {msg}")

    def task_recently_ran(script_path, minutes=60):
        try:
            mtime = os.path.getmtime(script_path)
            last_run = datetime.datetime.fromtimestamp(mtime)
            return (datetime.datetime.now() - last_run).total_seconds() < (minutes * 60)
        except FileNotFoundError:
            return False

    log("=== Skipped Task Recovery Agent Started ===")

    while True:
        for name, script in TASKS:
            if not task_recently_ran(script):
                log(f"{name} missing or stale — running now.")
                try:
                    subprocess.run(["python3", script], check=True)
                except Exception as e:
                    log(f"Error running {name}: {e}")
            else:
                log(f"{name} is up to date.")
        time.sleep(600)  # check every 10 minutes
""")

# === Create scripts ===
scripts_to_create = {
    "log_fitness_heartbeat.py": make_heartbeat_script("fitness_heartbeat.log", "Fitness heartbeat logged successfully"),
    "log_geofence_heartbeat.py": make_heartbeat_script("geofence_heartbeat.log", "Geofence heartbeat logged successfully"),
    "log_voice_reminder_heartbeat.py": make_heartbeat_script("voice_reminder_heartbeat.log", "Voice reminder heartbeat logged successfully"),
    "skipped_task_recovery.py": skipped_task_recovery
}

os.makedirs(TOOLS_DIR, exist_ok=True)

for filename, content in scripts_to_create.items():
    path = os.path.join(TOOLS_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    os.chmod(path, stat.S_IRWXU)  # make executable
    print(f"Deployed {filename} → {path}")

print("\nAll missing heartbeat scripts and skipped-task recovery agent deployed.")
print("To run skipped task recovery in background:")
print(f"nohup python3 {os.path.join(TOOLS_DIR, 'skipped_task_recovery.py')} &")
