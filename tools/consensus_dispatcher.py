#!/usr/bin/env python3
import argparse, subprocess, json, yaml, os, datetime
def now(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def run(cmd, dry=False):
    if dry: return 0, "DRYRUN: " + cmd, ""
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", choices=["am","pm","monthly","weekly","all"], default=os.environ.get("WINDOW","all"))
    ap.add_argument("--registry", default=os.environ.get("CONSENSUS_REGISTRY","CONSENSUS_REGISTRY.yaml"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    reg = yaml.safe_load(open(args.registry))
    results=[]
    for t in reg.get("tasks", []):
        if args.window!="all" and t.get("window")!=args.window: continue
        rc,out,err = run(t.get("command","true"), args.dry_run)
        results.append({"ts":now(),"feature_id":t["feature_id"],"title":t["title"],"window":t["window"],"rc":rc,"stdout":out.strip(),"stderr":err.strip()})
    print(json.dumps({"ran":len(results),"window":args.window,"results":results}, indent=2))
if __name__=="__main__": main()
