"""Milestone 21: frozen M20 proposal, out-of-family robustness evaluation.

Uses an independently written queue-relaxation shortest-path oracle.
These generated tests are not an independently sourced scientific benchmark.
"""
from __future__ import annotations
import argparse
from collections import deque
import json
import random
from pathlib import Path

from milestone20_planner import RecordedProposalProvider, bounded_search, validate, sha
from solo_vs_team_planning import GRID_SIZE, make_grid

FAMILIES=("legacy_distribution","sparse_low_cost","dense_low_cost","cost_bands")
SEEDS=tuple(range(61000,61064))
MAX_CASES=len(FAMILIES)*len(SEEDS)
PROTOCOL="m21_robustness_frozen_m20"
_PREVIOUS=range(30000,30064)

def create_case(family, seed):
    if family not in FAMILIES or type(seed) is not int:
        raise ValueError("Unsupported evaluation family or seed")
    if family=="legacy_distribution":
        return make_grid(seed)
    r=random.Random(100000*FAMILIES.index(family)+seed)
    out=[]
    for y in range(GRID_SIZE):
        row=[]
        for x in range(GRID_SIZE):
            if family=="sparse_low_cost":
                blocked=r.random()<0.08
                cost=r.randint(1,2)
            elif family=="dense_low_cost":
                blocked=r.random()<0.32
                cost=r.randint(1,3)
            else:
                blocked=r.random()<0.12
                cost=1 if (x+y)%4<2 else r.randint(4,9)
            row.append(None if blocked else cost)
        out.append(row)
    # Guarantee at least one route via top row and right edge.
    for x in range(GRID_SIZE):
        if out[0][x] is None:out[0][x]=r.randint(1,2)
    for y in range(GRID_SIZE):
        if out[y][-1] is None:out[y][-1]=r.randint(1,2)
    return tuple(tuple(row) for row in out)

def oracle_relaxation(grid):
    """Independent queue-relaxation oracle, not reusing candidate heap logic."""
    n=GRID_SIZE
    if len(grid)!=n or any(len(row)!=n for row in grid):raise ValueError("Bad grid")
    start=(0,0)
    end=(n-1,n-1)
    if grid[0][0] is None or grid[-1][-1] is None:
        raise ValueError("Blocked endpoint")
    distances={start:0}
    queue=deque([start])
    pending={start}
    relaxations=0
    while queue:
        x,y=queue.popleft()
        pending.remove((x,y))
        for nx,ny in ((x,y+1),(x+1,y),(x,y-1),(x-1,y)):
            if nx<0 or ny<0 or nx>=n or ny>=n or grid[ny][nx] is None:
                continue
            proposal=distances[(x,y)]+grid[ny][nx]
            if proposal<distances.get((nx,ny),float("inf")):
                distances[(nx,ny)]=proposal
                relaxations+=1
                if relaxations>n*n*n*n:
                    raise RuntimeError("Oracle runaway")
                if (nx,ny) not in pending:
                    pending.add((nx,ny))
                    queue.append((nx,ny))
    return distances.get(end)

def fixed_specs():
    p=validate(RecordedProposalProvider().propose())
    return p["candidates"]

def evaluate():
    if set(SEEDS)&set(_PREVIOUS):
        raise ValueError("Old holdout seed reused")
    specs=fixed_specs()
    records=[]
    for family in FAMILIES:
        for seed in SEEDS:
            grid=create_case(family,seed)
            optimal=oracle_relaxation(grid)
            for spec in specs:
                observed=bounded_search(grid,spec)
                cost=observed["cost"]
                records.append({
                    "family":family,"seed":seed,"candidate":spec["id"],
                    "oracle_cost":optimal,"candidate_cost":cost,
                    "correct":cost==optimal and optimal is not None,
                    "expansions":observed["expansions"],
                    "regret":None if cost is None or optimal is None else cost-optimal
                })
    summaries={}
    for family in FAMILIES:
        summaries[family]={}
        for spec in specs:
            rows=[x for x in records if x["family"]==family and x["candidate"]==spec["id"]]
            incorrect=[x for x in rows if not x["correct"]]
            summaries[family][spec["id"]]={
                "total":len(rows),"optimal":len(rows)-len(incorrect),
                "mean_expansions":round(sum(x["expansions"] for x in rows)/len(rows),3),
                "max_regret":max((x["regret"] for x in rows if x["regret"] is not None),default=None),
                "first_three_failures":[{"seed":x["seed"],"oracle_cost":x["oracle_cost"],
                    "candidate_cost":x["candidate_cost"]} for x in incorrect[:3]]
            }
    # Do not use these results to select a replacement candidate;
    # this run is a report on the already-frozen previous candidate.
    weighted=[summaries[f]["candidate_b"] for f in FAMILIES]
    return {"protocol":PROTOCOL,"selection_frozen_from_m20":"candidate_b",
            "evaluation_cases":MAX_CASES,"candidate_evaluations":len(records),
            "family_counts":{f:len(SEEDS) for f in FAMILIES},
            "seed_set_sha256":sha(SEEDS),
            "independent_oracle":"queue_relaxation_bellman_ford_style",
            "summaries":summaries,
            "selected_candidate_fully_optimal":all(x["optimal"]==x["total"] for x in weighted),
            "selected_candidate_failures":sum(x["total"]-x["optimal"] for x in weighted),
            "proposal_training_or_tuning_performed":False,
            "research_promotion_approved":False,
            "production_changes":False,
            "real_ai_agents":0,
            "limitations":[
                "Internally generated families are not independent externally labeled data",
                "The same recorded M20 proposal is evaluated; no new autonomous proposal",
                "Previously selected heuristic is not universally optimal",
                "No live model invocation, AI training, or recursive improvement"
            ]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=evaluate()
    data=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output:
        if args.output.is_symlink() or not args.output.parent.is_dir():
            raise ValueError("Output directory unavailable")
        args.output.write_text(data,encoding="utf8")
    print(data,end="")
if __name__=="__main__":main()
