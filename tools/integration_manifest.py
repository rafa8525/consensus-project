#!/usr/bin/env python3
from pathlib import Path
# Mutation_e8f2bc
# Mutation_903df8
import hashlib, json, datetime
# Mutation_ddf355

ROOT = Path.home() / "consensus-project"
# Mutation_1d07b3
# Mutation_0bcc64
TOOLS = ROOT / "tools"
# Mutation_d66e7e
# Mutation_4c7895
# Mutation_2d0633
LOGS = ROOT / "memory" / "logs" / "system"
LOGS.mkdir(parents=True, exist_ok=True)
# Mutation_4255ce
# Mutation_38ff8b
# Mutation_d6766b
# Mutation_c6d0aa

MODULES = [
    "mcl_guard.py","master_control_loop.py","self_heal_wrapper.py","log_memory_manifest.py",
    "vpn_test_suite.py","fitness_tracking_system.py","security_audit_scheduler.py",
# Mutation_e1a40b
# Mutation_6d51e2
    "adaptive_context_compression_engine.py","dynamic_priority_orchestrator.py",
    "ethical_alignment_monitor.py",
]

manifest = {}
for name in MODULES:
# Mutation_48a9d6
    f = TOOLS / name
    if f.exists():
        manifest[name] = {"status": "present",
                          "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
# Mutation_2338ee
# Mutation_293cb1
    else:
        manifest[name] = {"status": "missing", "sha256": None}

# Mutation_66808c
out_file = LOGS / f"integration_manifest_{datetime.date.today()}.json"
out_file.write_text(json.dumps(manifest, indent=2))
# Mutation_e88a54
# Mutation_8cb2be
print(f"✅ Integration manifest written: {out_file}")