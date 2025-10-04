#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import csv, statistics, re, yaml
ROOT=Path.home()/ "consensus-project"; DATA=ROOT/"memory"/"logs"/"sports"/"data"; OUT=ROOT/"memory"/"logs"/"sports"; OUT.mkdir(parents=True, exist_ok=True); CONF=ROOT/"config"/"sports"/"teams.yaml"
def team_form(league, team, last_n=5):
    f = DATA/league/(re.sub(r'[^A-Za-z0-9]+','_',team)+".csv")
    if not f.exists(): return None
    rows=[]
    for r in csv.DictReader(f.open(encoding="utf-8")):
        try: rows.append(int(r["for"])-int(r["against"]))
        except: pass
    rows = rows[-last_n:] if rows else []
    return statistics.fmean(rows) if rows else None
def predict(form):
    if form is None: return ("unknown", 0.50)
    p=0.50+ max(-0.30, min(0.30, form/20.0))
    return ("win" if p>=0.50 else "loss", max(0.05, min(0.95, abs(p))))
def main():
    cfg=yaml.safe_load(open(CONF, "r", encoding="utf-8")) or {}; today=datetime.now().strftime("%Y-%m-%d")
    for league, teams in cfg.items():
        for team in teams:
            form=team_form(league, team); pick, conf = predict(form)
            name=f"{league}_{re.sub(r'[^A-Za-z0-9]+','_',team)}_{today}.md"
            (OUT/name).write_text("\n".join([f"# {team} — {league.upper()} prediction ({today})",
                                             f"- recent_form: {form if form is not None else 'none'}",
                                             f"- pick: {pick}",
                                             f"- confidence: {conf:.2f}",
                                             f"- note: {'low-confidence (add CSV data to improve)' if form is None else 'based on last-5 point/run diff'}",
                                             ""]) , encoding="utf-8")
            print(f"Wrote {OUT/name}")
if __name__=="__main__": main()
