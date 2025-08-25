#!/usr/bin/env python3
import os, sys, json, subprocess
try:
    import yaml
except ImportError:
    print("Missing PyYAML: pip install pyyaml", file=sys.stderr); sys.exit(2)

REG_PATH = os.environ.get("CONSENSUS_REGISTRY", "CONSENSUS_REGISTRY.v2a.yaml")
WINDOW   = os.environ.get("WINDOW", "am")

def load_registry(path):
    with open(path, 'r', encoding='utf-8') as f:
        reg = yaml.safe_load(f) or []
    # Allow: (A) top-level list; (B) {"tasks": [...]} mapping
    if isinstance(reg, list):
        tasks = reg
    elif isinstance(reg, dict):
        tasks = reg.get("tasks", [])
    else:
        tasks = []
    # normalize task dicts
    return [t for t in tasks if isinstance(t, dict)]

def run_task(t):
    cmd = t.get("command")
    if not cmd:
        return 0, "", ""
    # shell= True so your existing commands work as-is
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def main():
    tasks = load_registry(REG_PATH)
    to_run = [t for t in tasks if t.get("window") == WINDOW]
    results = []
    for t in to_run:
        rc, out, err = run_task(t)
        results.append({
            "ts": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "feature_id": t.get("feature_id",""),
            "title": t.get("title",""),
            "window": t.get("window",""),
            "rc": rc,
            "stdout": out.strip(),
            "stderr": err.strip(),
        })
    print(json.dumps({"ran": len(to_run), "window": WINDOW, "results": results}, indent=2))

if __name__ == "__main__":
    main()
