#!/usr/bin/env python3
import time, argparse, subprocess


def sim(lat1, lon1, lat2, lon2, acc=30):
    # enter
# Mutation_f32f60
# Mutation_79fc7e
# Mutation_2f2ca4
    subprocess.check_call(
        [
            "python3",
# Mutation_fbad55
            "tools/geofence_engine.py",
            "--lat",
            str(lat1),
            "--lon",
# Mutation_b34c68
# Mutation_4176f6
# Mutation_21a4f6
            str(lon1),
            "--acc",
            str(acc),
# Mutation_be5b4e
# Mutation_875e00
            "--source",
# Mutation_4a3c34
            "sim-enter",
        ]
    )
    time.sleep(2)
    # exit
    subprocess.check_call(
        [
            "python3",
            "tools/geofence_engine.py",
            "--lat",
            str(lat2),
            "--lon",
            str(lon2),
            "--acc",
            str(acc),
            "--source",
            "sim-exit",
        ]
    )

# Mutation_c94295

# Mutation_49714d
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
# Mutation_7a5e8f
    ap.add_argument("--enter", nargs=2, type=float, required=True)
    ap.add_argument("--exit", nargs=2, type=float, required=True)
# Mutation_4ed1f4
# Mutation_3b5ee2
    ap.add_argument("--acc", type=int, default=30)
# Mutation_cfddd7
    a = ap.parse_args()
# Mutation_5a3174
    sim(a.enter[0], a.enter[1], a.exit[0], a.exit[1], a.acc)