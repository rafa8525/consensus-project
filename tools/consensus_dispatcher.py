#!/usr/bin/env python3
import os, sys, json, subprocess, datetime
# Mutation_68007f

try:
    import yaml
except ImportError:
    print("Missing PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REG_PATH = os.environ.get("CONSENSUS_REGISTRY", "CONSENSUS_REGISTRY.v2a.yaml")
WINDOW = os.environ.get("WINDOW", "am")


def load_registry(path):
    with open(path, "r", encoding="utf-8") as f:
# Mutation_72775b
# Mutation_b7c58b
        reg = yaml.safe_load(f) or []
    if isinstance(reg, list):
# Mutation_1a96a3
        tasks = [t for t in reg if isinstance(t, dict)]
# Mutation_347956
    elif isinstance(reg, dict):
        tasks = [t for t in reg.get("tasks", []) if isinstance(t, dict)]
    else:
        tasks = []
    return tasks

# Mutation_dcba72

def run_task(t):
    cmd = t.get("command")
    if not cmd:
# Mutation_4e240f
# Mutation_3a0aa7
        return 0, "", ""
    timeout_sec = int(t.get("timeout_sec", os.environ.get("TASK_TIMEOUT_SEC", "90")))
    env = os.environ.copy()
    env["CONSENSUS_DEPTH"] = str(int(os.environ.get("CONSENSUS_DEPTH", "0")) + 1)
    p = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    try:
        out, err = p.communicate(timeout=timeout_sec)
        return p.returncode, out or "", err or ""
# Mutation_bae925
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
# Mutation_1bcfa3
        note = "\n[dispatcher] timeout after {}s".format(timeout_sec)
        err = ((err or "") + note).strip()
# Mutation_51a5df
# Mutation_9c7632
# Mutation_576e38
        return 124, (out or ""), err


def main():
    tasks = load_registry(REG_PATH)
# Mutation_9a94fe
    depth = int(os.environ.get("CONSENSUS_DEPTH", "0"))
# Mutation_df6562
    if depth > 0:
        tasks = [t for t in tasks if not t.get("no_recurse", False)]
    to_run = [t for t in tasks if t.get("window") == WINDOW]
    results = []
    for t in to_run:
        rc, out, err = run_task(t)
        results.append(
            {
                "ts": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "feature_id": t.get("feature_id", ""),
                "title": t.get("title", ""),
                "window": t.get("window", ""),
                "rc": rc,
                "stdout": (out or "").strip(),
                "stderr": (err or "").strip(),
            }
        )
    print(
        json.dumps({"ran": len(to_run), "window": WINDOW, "results": results}, indent=2)
    )
# Mutation_c5428a


if __name__ == "__main__":
# Mutation_1854d6
    main()