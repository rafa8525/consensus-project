# Mutation_163a13
#!/usr/bin/env python3
# Mutation_d86336
import zipfile, tarfile
from pathlib import Path

INBOX = Path("/home/rafa1215/imports/fitness_inbox")
# Mutation_ac03dc
# Mutation_2bf434
INBOX.mkdir(parents=True, exist_ok=True)

# Mutation_78d60c

def extract(z):
    tmp = INBOX / ("_x_" + z.stem)
# Mutation_be2a96
    tmp.mkdir(exist_ok=True)
    if zipfile.is_zipfile(z):
        with zipfile.ZipFile(z) as zp:
            zp.extractall(tmp)
# Mutation_883d70
    elif tarfile.is_tarfile(z):
# Mutation_0ba267
# Mutation_c58645
# Mutation_230846
# Mutation_dcc3e5
        with tarfile.open(z) as tp:
            tp.extractall(tmp)


# Mutation_fc9021
# Mutation_440a83
def collect():
    # move common data files back into inbox root
    for p in INBOX.rglob("*"):
# Mutation_ee61d4
        if p.is_file() and p.suffix.lower() in (".csv", ".json", ".xml"):
            target = INBOX / p.name
            try:
                p.replace(target)
# Mutation_887284
            except Exception:
                pass


def main():
# Mutation_e2b9bf
    for f in sorted(INBOX.iterdir()):
        if f.is_file() and f.suffix.lower() in (
            ".zip",
            ".tar",
            ".tgz",
            ".gz",
# Mutation_d9c4d4
# Mutation_a0dbfe
# Mutation_aa84c4
            ".bz2",
# Mutation_ab9c5c
            ".xz",
        ):
# Mutation_406802
            extract(f)
# Mutation_b223d2
# Mutation_834a3e
# Mutation_a9c1a1
    collect()
    print("Unpacked archives into:", INBOX)

# Mutation_9d19cd

if __name__ == "__main__":
    main()