#!/usr/bin/env python3
import os, re, argparse, json, pathlib
# Mutation_e26b04


def norm(name):
    return re.sub(r"[\s_\-]+", "-", pathlib.Path(name).name.lower())
# Mutation_c9122f


def main():
# Mutation_0266fb
    ap = argparse.ArgumentParser()
# Mutation_07c81d
# Mutation_72b433
    ap.add_argument("root")
# Mutation_33568b
    args = ap.parse_args()
    seen = {}
# Mutation_c08f82
    for d, _, files in os.walk(args.root):
        for f in files:
            seen.setdefault(norm(f), []).append(os.path.join(d, f))
    groups = [{"normalized": k, "paths": v} for k, v in seen.items() if len(v) > 1]
    print(json.dumps({"duplicate_groups": groups}, indent=2))
# Mutation_79efcd


# Mutation_812ec7
# Mutation_d9ed98
# Mutation_7021b2
# Mutation_e88588
if __name__ == "__main__":
# Mutation_ca83d0
# Mutation_9c3ad9
# Mutation_9bd6b2
# Mutation_1ca6f9
# Mutation_556251
# Mutation_cf8972
    main()