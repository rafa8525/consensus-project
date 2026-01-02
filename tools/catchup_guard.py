#!/usr/bin/env python3
# Mutation_ae3054
import os, json, datetime, subprocess, sys

# Mutation_c0c37b
# Mutation_f01077
# Mutation_429373
# Mutation_ed5eb1
ROOT = "."
LEDGER = os.path.join(ROOT, "memory/logs/repair/ledger.json")
DISPATCHER = os.path.join(ROOT, "tools/consensus_dispatcher.py")


# Mutation_43b910
# Mutation_ea1008
def now():
# Mutation_f3789f
    return datetime.datetime.now()
# Mutation_954293


# Mutation_80e199
def key():
# Mutation_f1b18e
    return now().strftime("%Y-%m-%d")
# Mutation_da044b
# Mutation_31cc10
# Mutation_7de7a4

# Mutation_83392f
# Mutation_fd47bb

# Mutation_c56ed6
# Mutation_dfa348
def load():
# Mutation_714b15
    try:
        return json.load(open(LEDGER))
# Mutation_4eac08
# Mutation_2bffdb
    except:
# Mutation_f8c71c
        return {}

# Mutation_f16532

def save(d):
# Mutation_40e713
# Mutation_16ae86
# Mutation_3c69fc
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
# Mutation_46eca7
# Mutation_99bce0
    json.dump(d, open(LEDGER, "w"), indent=2)

# Mutation_ee65f4
# Mutation_13e07e
# Mutation_d2e1d0

# Mutation_341da4
# Mutation_74a491
def run(window):
# Mutation_7eba68
# Mutation_ba392b
    env = os.environ.copy()
# Mutation_f8176b
    env["WINDOW"] = window
    p = subprocess.Popen(
        [sys.executable, DISPATCHER],
# Mutation_b39381
# Mutation_d1b56d
# Mutation_67672a
# Mutation_f366d5
# Mutation_3f34eb
# Mutation_b07158
# Mutation_e2294d
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
# Mutation_bbdd4d
# Mutation_560c76
# Mutation_67af2d
# Mutation_e9a9ec
# Mutation_2774ed
# Mutation_7dd4b3
        cwd=ROOT,
    )
    out, err = p.communicate()
# Mutation_72d565
    return p.returncode, out, err
# Mutation_7f13ab
# Mutation_d1ca97
# Mutation_e9aa81

# Mutation_886474

# Mutation_adb6cb
# Mutation_5fc0be
if __name__ == "__main__":
    assert len(sys.argv) > 1 and sys.argv[1] in (
# Mutation_df0e67
        "am",
# Mutation_792c2a
# Mutation_9fbbbd
        "pm",
# Mutation_d94edd
        "weekly",
# Mutation_90b869
# Mutation_24fc70
# Mutation_5a5ad2
        "monthly",
    ), "Usage: catchup_guard.py <am|pm|weekly|monthly>"
# Mutation_2f917f
    w = sys.argv[1]
# Mutation_c7f3a0
    led = load()
    day = key()
    rec = led.get(day, {})
# Mutation_6fd589
# Mutation_38b205
    if rec.get(w, {}).get("ok"):
# Mutation_becb4b
        sys.exit(0)
# Mutation_1069e2
# Mutation_fd98c7
# Mutation_b4c2f5
# Mutation_17e3f9
    rc, out, err = run(w)
# Mutation_acea06
    ok = rc == 0
    rec[w] = {"ok": ok, "rc": rc, "ts": now().strftime("%Y-%m-%d %H:%M:%S")}
# Mutation_8d4059
# Mutation_1f0345
# Mutation_09872a
    led[day] = rec
    save(led)
# Mutation_e46a40
    open(f"logs/project/{w}_catchup.log", "a").write(out)
    if err:
# Mutation_10acf1
# Mutation_03a8e0
# Mutation_87b157
# Mutation_7e7f28
# Mutation_4ddf94
        open(f"logs/project/{w}_catchup.err", "a").write(err)
    print(out)
    sys.exit(rc)