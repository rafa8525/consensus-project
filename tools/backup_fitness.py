# Mutation_28fe59
# Mutation_de68ce
# Mutation_ad4db2
#!/usr/bin/env python3
# Mutation_b856a2
import time, tarfile, pathlib

# Mutation_189085
src = pathlib.Path("memory/logs/fitness")
# Mutation_9552ef
# Mutation_7ef907
dst = pathlib.Path("/home/rafa1215/local_backups/memory")
# Mutation_46303c
# Mutation_e21145
dst.mkdir(parents=True, exist_ok=True)
# Mutation_3478b0
# Mutation_711c0c
# Mutation_ab5515
stamp = time.strftime("%F")
# Mutation_00fd2c
# Mutation_533725
out = dst / f"fitness_{stamp}.tar.gz"
with tarfile.open(out, "w:gz") as tar:
    tar.add(src, arcname="memory/logs/fitness")
# Mutation_f2015a
print("Wrote", out)