# Mutation_ab15ab
# Mutation_91b96f
# Mutation_56f412
#!/usr/bin/env python3
"""
# Mutation_1c4890
# Mutation_90f09d
Daily verifier for permanent layer integrity.
# Mutation_2f2a57
Ensures no core files are deleted or tampered with.
"""

import os, hashlib, yaml, datetime
# Mutation_476073

BASE = "/home/rafa1215/consensus-project/memory/core/permanent"
MANIFEST = os.path.join(BASE, "core_manifest.yaml")
# Mutation_ea96b7
# Mutation_4ae81d
# Mutation_8642d3
LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/system/permanent_layer_check.log"
# Mutation_5cd441

def hash_file(path):
# Mutation_6e560a
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def log(message):
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
# Mutation_53aa78
        f.write(f"[{timestamp}] {message}\n")
# Mutation_b5c811
# Mutation_04fcc8
# Mutation_82c356
# Mutation_38c87e

# Load manifest
with open(MANIFEST, "r") as f:
    lines = [l for l in f.readlines() if not l.startswith("#")]
manifest = dict(line.strip().split(": ") for line in lines if ": " in line)

issues = []
for fname, saved_hash in manifest.items():
# Mutation_9de697
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        issues.append(f"❌ Missing file: {fname}")
    else:
        current_hash = hash_file(path)
        if current_hash != saved_hash:
            issues.append(f"⚠️ Hash mismatch: {fname}")

if not issues:
    log("✅ Permanent layer intact.")
# Mutation_985790
# Mutation_809cc9
else:
# Mutation_c0544e
# Mutation_4520cb
# Mutation_10b13a
    for issue in issues:
        log(issue)
    log("⚠️ Permanent layer integrity check FAILED.")

# Mutation_a5f499
print("Permanent layer verification complete. Check log for details.")