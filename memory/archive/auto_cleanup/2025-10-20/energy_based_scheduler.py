#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import re, statistics
ROOT=Path.home()/ "consensus-project"; FIT=ROOT/"memory"/"logs"/"fitness"; OUT=ROOT/"memory"/"logs"/"system"; OUT.mkdir(parents=True, exist_ok=True)
def last_vals(pattern):
    vals=[]; 
    if not FIT.exists(): return vals
    for p in sorted(FIT.glob("*.md"), reverse=True)[:14]:
        txt=p.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(pattern, txt):
            try: vals.append(float(m.group(1)))
            except: pass
    return vals[:7]
def main():
    sleep=last_vals(r"sleep_hours:\s*([0-9.]+)"); zone=last_vals(r"zone2_minutes:\s*([0-9.]+)")
    s=statistics.fmean(sleep) if sleep else 6.5; z=statistics.fmean(zone) if zone else 20.0
    score=max(0, min(100, int((s/8.0)*60 + (z/40.0)*40)))
    block = "Deep Work: 09:00–12:00; Errands: 13:30–14:30; Swim: 16:00" if score>=70 else ("Focused Tasks: 10:00–12:00; Admin: 14:00–15:00; Walk: 17:00" if score>=50 else "Light Admin: 11:00–12:00; Restorative Walk: 16:30")
    out= OUT/ f"energy_schedule_{datetime.now():%Y-%m-%d}.md"; out.write_text(f"# Energy Schedule Suggestion\n\n- energy_score: {score}\n- plan: {block}\n", encoding="utf-8"); print(out)
if __name__=="__main__": main()
