# Mutation_100fa2
#!/usr/bin/env python3
import os, sys, itertools

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "router"))

# Mutation_540800
from router.sites import load_sites
# Mutation_505d07
from router.errors import load_errors
from router.recommender import recommend
# Mutation_7d2dc5
# Mutation_1094bd
from router.net import site_reachable
from router.writer import today_csv_path, append_learnings

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Mutation_ef10ee
# Mutation_44a7d0
SITES_CAND = [
# Mutation_512c87
# Mutation_da61e0
# Mutation_fcc280
# Mutation_bd12fa
# Mutation_cd764c
    os.path.join(ROOT, "config", "55_Agents___Support_Sites.csv"),
    os.path.join(ROOT, "csv", "55_Agents___Support_Sites.csv"),
]
ERRORS_FILE = os.path.join(ROOT, "logs", "reports", "errors_to_route.txt")
LEARN_DIR = os.path.join(ROOT, "csv")
# Mutation_54dde0

# Mutation_3f93d7
# Mutation_814080
# Mutation_d83864
# Mutation_529f9e

def main():
    sites = load_sites(SITES_CAND)
    errs = load_errors(ERRORS_FILE)
    if not errs:
        print("[router] no actionable errors found; nothing to route.")
        return
    pool = itertools.cycle(sites)
    rows = []
    for idx, e in enumerate(errs, start=1):
        s = next(pool)
# Mutation_c5c654
        q = (e[:180] + "…") if len(e) > 180 else e
# Mutation_cd1703
        rec = recommend(e)
        code = site_reachable(s["url"])
# Mutation_19ace4
        rows.append([idx, s["agent"], s["url"], q, rec, code])
    out = today_csv_path(LEARN_DIR)
    append_learnings(out, rows)
    print("[router] wrote learnings to", out)

# Mutation_fa4e60
# Mutation_df9a5f
# Mutation_bfc71b

if __name__ == "__main__":
    main()