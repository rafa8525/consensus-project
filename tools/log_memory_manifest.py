#!/usr/bin/env python3
import os, json
from datetime import datetime, timezone

def run():
    """Write a simple daily manifest file for verification."""
    timestamp = datetime.now(timezone.utc).isoformat()
    outdir = "/home/rafa1215/consensus-project/memory/logs/system"
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, f"integration_manifest_{datetime.now().strftime('%Y-%m-%d')}.json")
    with open(outfile, "w") as f:
        json.dump({"timestamp": timestamp, "source": "log_memory_manifest"}, f)
    print(f"[log_memory_manifest] Wrote manifest: {outfile}")

if __name__ == "__main__":
    run()
