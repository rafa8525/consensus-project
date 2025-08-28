#!/usr/bin/env python3
import time, tarfile, pathlib
src = pathlib.Path("memory/logs/fitness")
dst = pathlib.Path("/home/rafa1215/local_backups/memory")
dst.mkdir(parents=True, exist_ok=True)
stamp = time.strftime("%F")
out = dst / f"fitness_{stamp}.tar.gz"
with tarfile.open(out, "w:gz") as tar:
    tar.add(src, arcname="memory/logs/fitness")
print("Wrote", out)
