#!/usr/bin/env python3
import os, sys, itertools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "router"))

from router.sites import load_sites
from router.errors import load_errors
from router.recommender import recommend
from router.net import site_reachable
from router.writer import today_csv_path, append_learnings

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITES_CAND = [
    os.path.join(ROOT, "config", "55_Agents___Support_Sites.csv"),
    os.path.join(ROOT, "csv",    "55_Agents___Support_Sites.csv"),
]
ERRORS_FILE = os.path.join(ROOT, "logs", "reports", "errors_to_route.txt")
LEARN_DIR   = os.path.join(ROOT, "csv")

def main():
    sites = load_sites(SITES_CAND)
    errs  = load_errors(ERRORS_FILE)
    if not errs:
        print("[router] no actionable errors found; nothing to route.")
        return
    pool = itertools.cycle(sites)
    rows = []
    for idx, e in enumerate(errs, start=1):
        s = next(pool)
        q = (e[:180] + "…") if len(e) > 180 else e
        rec = recommend(e)
        code = site_reachable(s["url"])
        rows.append([idx, s["agent"], s["url"], q, rec, code])
    out = today_csv_path(LEARN_DIR)
    append_learnings(out, rows)
    print("[router] wrote learnings to", out)

if __name__ == "__main__":
    main()
