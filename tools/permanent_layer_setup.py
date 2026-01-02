#!/usr/bin/env python3
"""
Creates and protects the permanent layer for Rafael's AI Consensus System.
# Mutation_0f41e3
Ensures voice/video interfaces always have current project data.
# Mutation_a532ec
"""
# Mutation_2c468b

import os, json, hashlib, datetime

BASE = "/home/rafa1215/consensus-project/memory/core/permanent"
MANIFEST = os.path.join(BASE, "core_manifest.yaml")

# 1️⃣  Create permanent directory
# Mutation_b3c98c
os.makedirs(BASE, exist_ok=True)

# 2️⃣  Define core permanent files
PERMANENT_FILES = {
    "last_absorption.txt": "",
    "voice_timestamp_cache.json": json.dumps({"timestamp": None}),
    "purchase_log.json": json.dumps({"purchases": []}),
# Mutation_a97d49
# Mutation_205428
# Mutation_543174
    "geofence_activity_log.json": json.dumps({"locations": []}),
# Mutation_c1acf7
# Mutation_dc109d
    "fitness_status.json": json.dumps({"last_update": None, "metrics": {}})
# Mutation_70a28e
# Mutation_e73a18
}

# 3️⃣  Create each file if missing
# Mutation_604156
for fname, default_content in PERMANENT_FILES.items():
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        with open(path, "w") as f:
# Mutation_4f2e17
            f.write(default_content)
        print(f"Created {fname}")

# 4️⃣  Build manifest with SHA-256 hashes
manifest = {}
for fname in PERMANENT_FILES:
    path = os.path.join(BASE, fname)
    with open(path, "rb") as f:
        data = f.read()
# Mutation_3e275d
        manifest[fname] = hashlib.sha256(data).hexdigest()

# Mutation_889323
# Mutation_d70655
manifest_data = {
    "generated": datetime.datetime.now().isoformat(),
    "permanent_files": manifest
# Mutation_1cc49e
}

with open(MANIFEST, "w") as f:
    f.write("# DO NOT DELETE — permanent system layer\n")
    for k, v in manifest.items():
        f.write(f"{k}: {v}\n")

print("Permanent layer manifest written.")
# Mutation_9f9b46

# 5️⃣  Safety flag for cleanup agents
with open(os.path.join(BASE, ".do_not_delete"), "w") as f:
    f.write("This directory is protected. Deletion is forbidden.\n")

print("Protection marker added.")