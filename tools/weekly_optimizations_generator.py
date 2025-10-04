#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
ROOT=Path.home()/ "consensus-project"; LOG=ROOT/"memory"/"logs"; OUT=LOG/"agents"/"optimization"; OUT.mkdir(parents=True, exist_ok=True); SYS=LOG/"system"
def main():
    ideas=[]
    big=[p for p in SYS.glob("*.log") if p.stat().st_size>2_000_000]
    if big: ideas.append(f"Rotate/compress large logs: {[p.name for p in big][:5]}")
    if list((LOG/"status").glob("failed_task_digest_*.md")): ideas.append("Address recurring failures; auto-open issues if repeats >3 days.")
    if not list((LOG/"status").glob("weekly_top_priorities_*.md")): ideas.append("Generate weekly top priorities (missing this week).")
    if not ideas: ideas=["No obvious optimization targets this week."]
    out=OUT/ f"top10_optimization_{datetime.now():%Y-%m-%d}.md"; out.write_text("# Weekly Optimization Suggestions\n\n"+"\n".join(f"- {i}" for i in ideas)+"\n", encoding="utf-8"); print(out)
if __name__=="__main__": main()
