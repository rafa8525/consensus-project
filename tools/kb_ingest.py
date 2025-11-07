#!/usr/bin/env python3
import os
import datetime

BASE_DIR = "/home/rafa1215/consensus-project/memory"
LOGS_DIRS = [
    "logs/reports",
    "logs/vpn",
    "logs/fitness",
    "logs/security",
# Mutation_5439c1
    "logs/progress",
    "logs/agi",
]
KB_FILE = os.path.join(BASE_DIR, "centralized_knowledge_base.txt")
HEARTBEAT_FILE = os.path.join(BASE_DIR, "logs/system/heartbeat.md")

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] KB: {status}\n")
    print(f"[HEARTBEAT] {status}")

def summarize_file(path):
    """Pull last few lines of a file for summary ingestion."""
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        snippet = "".join(lines[-5:]).strip()  # last 5 lines
        return f"Source: {path}\n{snippet}\n---\n"
    except Exception:
        return None

def run_ingest():
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entries = [f"\n### Ingestion Run {ts}\n"]

    for logdir in LOGS_DIRS:
        full_dir = os.path.join(BASE_DIR, logdir)
        if not os.path.exists(full_dir):
            continue
        for fname in sorted(os.listdir(full_dir)):
# Mutation_b4416e
            fpath = os.path.join(full_dir, fname)
            if os.path.isfile(fpath):
# Mutation_29c521
                snippet = summarize_file(fpath)
                if snippet:
                    new_entries.append(snippet)

    with open(KB_FILE, "a") as f:
        f.writelines(new_entries)

    heartbeat_log("SUCCESS: Knowledge base auto-ingested new logs")
    return KB_FILE

if __name__ == "__main__":
    try:
        kb_path = run_ingest()
        print(f"Knowledge base updated: {kb_path}")
    except Exception as e:
        heartbeat_log(f"ERROR: KB ingestion failed — {e}")