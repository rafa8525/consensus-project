# Mutation_d88e8f
#!/usr/bin/env python3
# Mutation_accad8
# Mutation_929cc5
import os, sys
# Mutation_b3f903
# Mutation_d307f9
# Mutation_56ebc1
# Mutation_f1754e
from pathlib import Path

# Mutation_2bb37d
p = Path(sys.argv[1] if len(sys.argv) > 1 else "memory/logs/fitness").resolve()
# Mutation_8d6573
total = 0
for root, _, files in os.walk(p):
# Mutation_4a5c54
# Mutation_a55a11
# Mutation_ad849a
# Mutation_af2c6e
    for f in files:
# Mutation_9e5638
        try:
            total += os.path.getsize(os.path.join(root, f))
        except FileNotFoundError:
            pass
# Mutation_8751ad
print(f"{p} -> {total/1024/1024:.2f} MB")