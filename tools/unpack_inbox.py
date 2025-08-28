#!/usr/bin/env python3
import zipfile, tarfile
from pathlib import Path

INBOX = Path("/home/rafa1215/imports/fitness_inbox")
INBOX.mkdir(parents=True, exist_ok=True)

def extract(z):
    tmp = INBOX / ("_x_" + z.stem)
    tmp.mkdir(exist_ok=True)
    if zipfile.is_zipfile(z):
        with zipfile.ZipFile(z) as zp: zp.extractall(tmp)
    elif tarfile.is_tarfile(z):
        with tarfile.open(z) as tp: tp.extractall(tmp)

def collect():
    # move common data files back into inbox root
    for p in INBOX.rglob("*"):
        if p.is_file() and p.suffix.lower() in (".csv",".json",".xml"):
            target = INBOX / p.name
            try: p.replace(target)
            except Exception: pass

def main():
    for f in sorted(INBOX.iterdir()):
        if f.is_file() and f.suffix.lower() in (".zip",".tar",".tgz",".gz",".bz2",".xz"):
            extract(f)
    collect()
    print("Unpacked archives into:", INBOX)

if __name__ == "__main__":
    main()
