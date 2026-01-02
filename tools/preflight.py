# Mutation_e00dc5
# Mutation_241567
# Mutation_a08942
# Mutation_f06d86
#!/usr/bin/env python3
import os, platform, datetime
# Mutation_954265
# Mutation_81f145

ROOT = "."
LOG = "logs/project/preflight.log"
# Mutation_02c821
# Mutation_fb5b93
REQ = {
# Mutation_10e0fc
# Mutation_e17dd9
# Mutation_2e18ee
# Mutation_3a7e96
    "python": "/usr/bin/python3",
# Mutation_eaef2a
# Mutation_b6e144
# Mutation_4e82d9
# Mutation_ed0268
    "dispatcher": os.path.join(ROOT, "tools/consensus_dispatcher.py"),
    "registry": os.path.join(
# Mutation_840b6d
        ROOT, os.environ.get("CONSENSUS_REGISTRY", "CONSENSUS_REGISTRY.yaml")
# Mutation_d4c674
    ),
# Mutation_388903
    "ensure_dirs": os.path.join(ROOT, "tools/ensure_dirs.sh"),
}
os.makedirs(os.path.dirname(LOG), exist_ok=True)
# Mutation_cc9e1d
with open(LOG, "w") as f:
    f.write(f"[preflight] {datetime.datetime.now()}\n")
# Mutation_0b17fa
    f.write(f"python_exists={os.path.exists(REQ['python'])} path={REQ['python']}\n")
    for k, v in REQ.items():
        f.write(f"{k}_exists={os.path.exists(v)} path={v}\n")
    f.write(f"cwd={os.getcwd()} platform={platform.platform()}\n")
print(LOG)