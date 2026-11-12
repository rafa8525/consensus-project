#!/usr/bin/env python3
"""Create an immutable, private snapshot of dirty tracked runtime files.
No live file is removed, rewritten, staged, committed or stashed.
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO=Path.home()/"consensus-project"
SAFE_PREFIXES=("memory/","logs/")
DEST=Path.home()/".local"/"share"/"ai-consensus"/"runtime-snapshots"
def run(*args):
    return subprocess.run(["git",*args],cwd=REPO,text=True,capture_output=True,timeout=90,check=False)
def paths():
    p=run("diff","--name-only","-z","--")
    if p.returncode: raise RuntimeError("git diff inspection failed")
    return sorted(set(x for x in p.stdout.split("\0") if x.startswith(SAFE_PREFIXES)))
def snapshot(dry_run=True):
    files=paths()
    if dry_run:
        return {"mode":"dry-run","files":files,"file_count":len(files),"mutated":False}
    DEST.mkdir(parents=True,exist_ok=True)
    os.chmod(DEST,0o700)
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target=Path(tempfile.mkdtemp(prefix=stamp+"-",dir=DEST))
    os.chmod(target,0o700)
    manifest={"created_utc":stamp,"source":str(REPO),"files":[]}
    for relative in files:
        src=REPO/relative
        if not src.is_file() or src.is_symlink():
            raise RuntimeError("Unsupported source path: "+relative)
        dst=target/relative
        dst.parent.mkdir(parents=True,exist_ok=True)
        with src.open("rb") as infile, dst.open("xb") as outfile:
            h=hashlib.sha256()
            while True:
                block=infile.read(1024*1024)
                if not block:break
                h.update(block); outfile.write(block)
        os.chmod(dst,0o600)
        manifest["files"].append({"path":relative,"sha256":h.hexdigest(),"bytes":dst.stat().st_size})
    result=target/"manifest.json"
    result.write_text(json.dumps(manifest,indent=2)+"\n")
    os.chmod(result,0o600)
    return {"mode":"snapshot","location":str(target),"files_saved":len(files),"mutated_live_files":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--apply",action="store_true",help="Create a local private snapshot; preserve originals")
    args=p.parse_args()
    print(json.dumps(snapshot(dry_run=not args.apply),indent=2))
if __name__=="__main__": main()
