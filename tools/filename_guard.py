#!/usr/bin/env python3
import os, re, argparse, json, pathlib
def norm(name): return re.sub(r'[\s_\-]+','-', pathlib.Path(name).name.lower())
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("root"); args=ap.parse_args()
    seen={}
    for d,_,files in os.walk(args.root):
        for f in files: seen.setdefault(norm(f), []).append(os.path.join(d,f))
    groups=[{"normalized":k,"paths":v} for k,v in seen.items() if len(v)>1]
    print(json.dumps({"duplicate_groups":groups}, indent=2))
if __name__=="__main__": main()
