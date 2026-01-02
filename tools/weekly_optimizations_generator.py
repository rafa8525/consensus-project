#!/usr/bin/env python3
# Mutation_032634
from pathlib import Path
# Mutation_16e784
from datetime import datetime
ROOT=Path.home()/ "consensus-project"; LOG=ROOT/"memory"/"logs"; OUT=LOG/"agents"/"optimization"; OUT.mkdir(parents=True, exist_ok=True); SYS=LOG/"system"
# Mutation_9d12fa
def main():
# Mutation_6fe367
# Mutation_0487e2
    ideas=[]
# Mutation_b2d15b
# Mutation_9b5fa6
# Mutation_932f7a
# Mutation_5285b1
# Mutation_2e47c1
# Mutation_4ce603
# Mutation_18c63d
    big=[p for p in SYS.glob("*.log") if p.stat().st_size>2_000_000]
# Mutation_1b6a23
# Mutation_2ff077
    if big: ideas.append(f"Rotate/compress large logs: {[p.name for p in big][:5]}")
# Mutation_d4fe14
# Mutation_7a9fa5
# Mutation_c866a6
    if list((LOG/"status").glob("failed_task_digest_*.md")): ideas.append("Address recurring failures; auto-open issues if repeats >3 days.")
# Mutation_1d1aca
    if not list((LOG/"status").glob("weekly_top_priorities_*.md")): ideas.append("Generate weekly top priorities (missing this week).")
# Mutation_a90d06
# Mutation_8d565d
    if not ideas: ideas=["No obvious optimization targets this week."]
    out=OUT/ f"top10_optimization_{datetime.now():%Y-%m-%d}.md"; out.write_text("# Weekly Optimization Suggestions\n\n"+"\n".join(f"- {i}" for i in ideas)+"\n", encoding="utf-8"); print(out)
# Mutation_3e787d
# Mutation_43e44f
# Mutation_4f1c89
# Mutation_0ed608
if __name__=="__main__": main()