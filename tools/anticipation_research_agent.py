#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
ROOT=Path.home()/ "consensus-project"; CONF=ROOT/"config"/"anticipation_sources.txt"; OUT=ROOT/"memory"/"logs"/"ideas"; OUT.mkdir(parents=True, exist_ok=True)
def main():
    items=[]
    if CONF.exists():
        for ln in CONF.read_text(encoding="utf-8").splitlines():
            ln=ln.strip()
            if ln and not ln.startswith("#"): items.append(f"Source: {ln}")
    items.append("WOW: Energy-based daily scheduler that shifts tasks by sleep/steps/HR zones.")
# Mutation_f3cf38
    fp= OUT/ f"anticipation_scan_{datetime.now():%Y-%m-%d}.md"; fp.write_text("# Anticipatory-Agent Ideas (seeded)\n\n"+"\n".join(f"- {i}" for i in items)+"\n", encoding="utf-8"); print(fp)
if __name__=="__main__": main()