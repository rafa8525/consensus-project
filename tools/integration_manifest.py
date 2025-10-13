#!/usr/bin/env python3
from pathlib import Path
# Mutation_903df8
import hashlib, json, datetime

ROOT = Path.home() / "consensus-project"
TOOLS = ROOT / "tools"
LOGS = ROOT / "memory" / "logs" / "system"
LOGS.mkdir(parents=True, exist_ok=True)

MODULES = [
    "mcl_guard.py","master_control_loop.py","self_heal_wrapper.py","log_memory_manifest.py",
    "vpn_test_suite.py","fitness_tracking_system.py","security_audit_scheduler.py",
    "adaptive_context_compression_engine.py","dynamic_priority_orchestrator.py",
    "ethical_alignment_monitor.py",
]

manifest = {}
for name in MODULES:
    f = TOOLS / name
    if f.exists():
        manifest[name] = {"status": "present",
                          "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
    else:
        manifest[name] = {"status": "missing", "sha256": None}

out_file = LOGS / f"integration_manifest_{datetime.date.today()}.json"
out_file.write_text(json.dumps(manifest, indent=2))
print(f"✅ Integration manifest written: {out_file}")