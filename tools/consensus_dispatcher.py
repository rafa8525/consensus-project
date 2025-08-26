#!/usr/bin/env python3
import os, sys, json, subprocess, datetime

try:
    import yaml
except ImportError:
    print("Missing PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REG_PATH = os.environ.get("CONSENSUS_REGISTRY", "CONSENSUS_REGISTRY.v2a.yaml")
WINDOW   = os.environ.get("WINDOW", "am")
def load_registry(path):
    with open(path, 'r', encoding='utf-8') as f:
        reg = yaml.safe_load(f) or []
    if isinstance(reg, list):
        tasks = [t for t in reg if isinstance(t, dict)]
    elif isinstance(reg, dict):
        tasks = [t for t in reg.get("tasks", []) if isinstance(t, dict)]
    else:
        tasks = []
    return tasks
def run_task(t):
    cmd = t.get("command")
    if not cmd:
        return 0, "", ""
    timeout_sec = int(t.get("timeout_sec", os.environ.get("TASK_TIMEOUT_SEC", "90")))
    env=os.environ.copy(); env['CONSENSUS_DEPTH']=str(int(os.environ.get('CONSENSUS_DEPTH','0'))+1)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    try:
        out, err = p.communicate(timeout=timeout_sec)
        return p.returncode, out or "", err or ""
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        note = "\n[dispatcher] timeout after {}s".format(timeout_sec)
        err = ((err or "") + note).strip()
        return 124, (out or ""), err
def main():
    tasks = load_registry(REG_PATH)
    depth = int(os.environ.get('CONSENSUS_DEPTH','0'))
    if depth>0:
        tasks = [t for t in tasks if not t.get('no_recurse', False)]
    to_run = [t for t in tasks if t.get("window") == WINDOW]
    results = []
    for t in to_run:
        rc, out, err = run_task(t)
        results.append({
            "ts": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "feature_id": t.get("feature_id",""),
            "title": t.get("title",""),
            "window": t.get("window",""),
            "rc": rc,
            "stdout": (out or "").strip(),
            "stderr": (err or "").strip(),
        })
    print(json.dumps({"ran": len(to_run), "window": WINDOW, "results": results}, indent=2))

if __name__ == "__main__":
    main()
