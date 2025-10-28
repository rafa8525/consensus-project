#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meta_evaluator.py
Purpose:
  Evaluates all agent manifests, compiles a summary of their last known
  actions, and writes a manifest index file to be used by higher-level
  evaluators and report builders.

Outputs:
  - logs/agents/meta_index.yaml
  - logs/agents/meta_summary.log
"""

import os
import yaml
from datetime import datetime

BASE_DIR = os.path.expanduser("~/consensus-project")
AGENT_LOG_DIR = os.path.join(BASE_DIR, "memory/logs/agents")
OUTPUT_DIR = os.path.join(BASE_DIR, "logs/agents")
INDEX_FILE = os.path.join(OUTPUT_DIR, "meta_index.yaml")
SUMMARY_FILE = os.path.join(OUTPUT_DIR, "meta_summary.log")

def gather_agent_manifests():
    manifest = []
    for root, _, files in os.walk(AGENT_LOG_DIR):
        for f in files:
            if not f.endswith(".md"):
                continue
            path = os.path.join(root, f)
            compress = os.path.getsize(path) > 100_000
            reason = "File large, suggested for compression" if compress else "OK"
            manifest.append({
                "file": os.path.relpath(path, BASE_DIR),
                "compress": compress,
                "reason": reason
            })
    return manifest

def write_manifest(manifest):
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        for item in manifest:
            f.write(f"- file: {item['file']}\n")
            f.write(f"  compress: {str(item['compress']).lower()}\n")
            if "reason" in item:
                f.write(f"  reason: \"{item['reason']}\"\n")

def write_summary(manifest):
    with open(SUMMARY_FILE, "w") as log:
        log.write(f"[meta-evaluator] Run: {datetime.now()}\n")
        log.write(f"Total agent files indexed: {len(manifest)}\n\n")
        large = [m for m in manifest if m["compress"]]
        if large:
            log.write("Large files flagged for compression:\n")
            for m in large:
                log.write(f" - {m['file']} ({m['reason']})\n")
        else:
            log.write("No large files detected.\n")

def main():
    print("[MetaEvaluator] Scanning agent logs...")
    manifest = gather_agent_manifests()
    print(f"[MetaEvaluator] Indexed {len(manifest)} files")
    write_manifest(manifest)
    write_summary(manifest)
    print(f"[MetaEvaluator] Wrote {INDEX_FILE}")
    print(f"[MetaEvaluator] Wrote {SUMMARY_FILE}")

if __name__ == "__main__":
    main()
