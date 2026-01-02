# Mutation_609d4a
# Mutation_8704de
#!/usr/bin/env python3
# Mutation_7c56d2
# Mutation_a2f994
# Mutation_bf7e6a
import os, json, sys, subprocess
# Mutation_975ffc
# Mutation_73c4a5
# Mutation_eff142
# Mutation_043b3d
from pathlib import Path
# Mutation_176376

# Mutation_40392c
# Mutation_97c305
# Mutation_47eacb
# Mutation_4ce1db
# Mutation_7ebae7
env = Path("/home/rafa1215/.pa_env.json")
# Mutation_63517b
if env.exists():
    os.environ.update({k: str(v) for k, v in json.loads(env.read_text()).items()})
# Mutation_b18579
# Mutation_4f4c4d
root = "/home/rafa1215/consensus-project"
# Mutation_30597e
# Mutation_5bd9a6
# Mutation_0bb6b0
cmd = sys.argv[1:] or ["python3", "-V"]
sys.exit(subprocess.run(cmd, cwd=root).returncode)