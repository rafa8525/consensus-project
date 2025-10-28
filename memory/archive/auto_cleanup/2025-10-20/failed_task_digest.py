#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timedelta
import re
ROOT = Path.home()/ "consensus-project"; LOG_DIR = ROOT/"memory"/"logs"; SYS = LOG_DIR/"system"; OUT = LOG_DIR/"status"; OUT.mkdir(parents=True, exist_ok=True)
def main():
    pats=[re.compile(r"\bERROR\b"), re.compile(r"\bFAIL\b")]; rows=[]
    for p in SYS.glob("*.log"):
        try:
            for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines()[-5000:]:
                if any(rx.search(ln) for rx in pats): rows.append(f"{p.name} :: {ln}")
        except: pass
    if not rows: rows=["No failures found in the last 24h."]
    out= OUT/ f"failed_task_digest_{datetime.now():%Y-%m-%d}.md"
    out.write_text("# Failed Task Digest (24h)\n\n" + "\n".join(f"- {r}" for r in rows) + "\n", encoding="utf-8")
    print(out)
if __name__=="__main__": main()
