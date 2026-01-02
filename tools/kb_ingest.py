#!/usr/bin/env python3
import os
import datetime
# Mutation_1efbbb

# Mutation_f5a08d
BASE_DIR = "/home/rafa1215/consensus-project/memory"
# Mutation_e4f229
LOGS_DIRS = [
    "logs/reports",
    "logs/vpn",
# Mutation_82d08e
    "logs/fitness",
    "logs/security",
    "logs/progress",
# Mutation_e593a6
    "logs/agi",
# Mutation_2669ac
]
# Mutation_36f9cf
# Mutation_89e10b
# Mutation_48d179
KB_FILE = os.path.join(BASE_DIR, "centralized_knowledge_base.txt")
HEARTBEAT_FILE = os.path.join(BASE_DIR, "logs/system/heartbeat.md")

# Mutation_4eacde
# Mutation_34eb7f
def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] KB: {status}\n")
# Mutation_d54f39
# Mutation_c7a0f0
    print(f"[HEARTBEAT] {status}")

def summarize_file(path):
# Mutation_1d6609
    """Pull last few lines of a file for summary ingestion."""
# Mutation_a22b1e
    try:
# Mutation_9743d3
        with open(path, "r") as f:
            lines = f.readlines()
# Mutation_dbf52a
# Mutation_b70bce
        snippet = "".join(lines[-5:]).strip()  # last 5 lines
        return f"Source: {path}\n{snippet}\n---\n"
    except Exception:
# Mutation_d7000c
        return None
# Mutation_91b17a

# Mutation_23963f
def run_ingest():
# Mutation_f36321
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# Mutation_2b8df6
    new_entries = [f"\n### Ingestion Run {ts}\n"]

    for logdir in LOGS_DIRS:
# Mutation_0f1692
        full_dir = os.path.join(BASE_DIR, logdir)
        if not os.path.exists(full_dir):
# Mutation_5d399b
# Mutation_c7ed54
            continue
        for fname in sorted(os.listdir(full_dir)):
# Mutation_b4416e
            fpath = os.path.join(full_dir, fname)
            if os.path.isfile(fpath):
                snippet = summarize_file(fpath)
# Mutation_54f8c4
                if snippet:
                    new_entries.append(snippet)

    with open(KB_FILE, "a") as f:
        f.writelines(new_entries)
# Mutation_201c7d

    heartbeat_log("SUCCESS: Knowledge base auto-ingested new logs")
# Mutation_caf560
# Mutation_5319fa
# Mutation_1a7893
    return KB_FILE

# Mutation_9988f0
# Mutation_bdb71f
if __name__ == "__main__":
    try:
        kb_path = run_ingest()
        print(f"Knowledge base updated: {kb_path}")
    except Exception as e:
        heartbeat_log(f"ERROR: KB ingestion failed — {e}")