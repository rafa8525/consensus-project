#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# Path to the full memory absorption log
FULL_MEMORY_LOG = "/home/rafa1215/consensus-project/memory/logs/heartbeat/full_memory_absorption.log"
LOOKUP_HEARTBEAT_LOG = "/home/rafa1215/consensus-project/memory/logs/heartbeat/voice_lookup_heartbeat.log"

def log_lookup(query, result_found):
    """Log every lookup with timestamp."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "FOUND" if result_found else "NOT FOUND"
    with open(LOOKUP_HEARTBEAT_LOG, "a", encoding="utf-8") as log:
        log.write(f"[{now}] Query: {query} | Result: {status}\n")

def search_memory(query):
    """Search for the query in the full memory absorption log."""
    if not os.path.exists(FULL_MEMORY_LOG):
        return None

    with open(FULL_MEMORY_LOG, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Case-insensitive search
    if query.lower() in content.lower():
        # Return surrounding context
        lines = content.splitlines()
        matched_lines = [line for line in lines if query.lower() in line.lower()]
        snippet = "\n".join(matched_lines[:10])  # Limit output to first 10 matches
        return snippet
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: voice_memory_lookup.py <search_query>")
        sys.exit(1)

    query = sys.argv[1]
    result = search_memory(query)

    if result:
        print(f"\n[RESULT for '{query}']\n{result}")
        log_lookup(query, True)
    else:
        print(f"\n[No results found for '{query}']")
        log_lookup(query, False)

if __name__ == "__main__":
    main()
