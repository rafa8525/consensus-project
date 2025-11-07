#!/usr/bin/env python3
"""
Daily verifier for permanent layer integrity.
Ensures no core files are deleted or tampered with.
"""

import os, hashlib, yaml, datetime

BASE = "/home/rafa1215/consensus-project/memory/core/permanent"
MANIFEST = os.path.join(BASE, "core_manifest.yaml")
LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/system/permanent_layer_check.log"

def hash_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def log(message):
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# Load manifest
with open(MANIFEST, "r") as f:
    lines = [l for l in f.readlines() if not l.startswith("#")]
manifest = dict(line.strip().split(": ") for line in lines if ": " in line)

issues = []
for fname, saved_hash in manifest.items():
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        issues.append(f"❌ Missing file: {fname}")
    else:
        current_hash = hash_file(path)
        if current_hash != saved_hash:
            issues.append(f"⚠️ Hash mismatch: {fname}")

if not issues:
    log("✅ Permanent layer intact.")
else:
    for issue in issues:
        log(issue)
    log("⚠️ Permanent layer integrity check FAILED.")

print("Permanent layer verification complete. Check log for details.")
