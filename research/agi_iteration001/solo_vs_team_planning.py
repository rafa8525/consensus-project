"""Milestone 19: controlled single-worker vs three-role planning experiment.

Deterministic algorithms and generated weighted grids, NOT AI agents or AGI.
Both arms receive identical proposals, data and search-evaluation budgets.
"""
from __future__ import annotations
import argparse
import hashlib
import heapq
import json
import random
from pathlib import Path

SEEDS_DEV=tuple(range(1000,1024))
SEEDS_TEST=tuple(range(9000,9064))
GRID_SIZE=12
CANDIDATES=("dijkstra","astar_manhattan","astar_weighted")
WEIGHTS={"dijkstra":0.0,"astar_manhattan":1.0,"astar_weighted":1.5}
PROTOCOL="solo_vs_three_roles_weighted_grid_v1"
MAX_EXPANSIONS=GRID_SIZE*GRID_SIZE
START=(0,0)
GOAL=(GRID_SIZE-1,GRID_SIZE-1)

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"))

def checksum(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()

def make_grid(seed):
    """A fixed random generator creates obstacles + strictly positive costs."""
    rng=random.Random(seed)
    grid=[]
    for y in range(GRID_SIZE):
        row=[]
        for x in range(GRID_SIZE):
            blocked = rng.random()<0.20
            value=rng.randint(1,9)
            row.append(None if blocked else value)
        grid.append(row)
    # Make at least one valid route (top row + rightmost column).
    for x in range(GRID_SIZE):
        if grid[0][x] is None:grid[0][x]=rng.randint(1,9)
    for y in range(GRID_SIZE):
        if grid[y][-1] is None:grid[y][-1]=rng.randint(1,9)
    return tuple(tuple(row) for row in grid)

def search(grid,variant):
    if variant not in WEIGHTS:raise ValueError("Unknown search proposal")
    if len(grid)!=GRID_SIZE or any(len(row)!=GRID_SIZE for row in grid):
        raise ValueError("Invalid graph")
    if grid[0][0] is None or grid[-1][-1] is None:
        raise ValueError("Blocked endpoint")
    # Counting each popped, previously unexpanded node once.
    weight=WEIGHTS[variant]
    h=lambda p:weight*(abs(GOAL[0]-p[0])+abs(GOAL[1]-p[1]))
    heap=[(h(START),0,START)]
    best={START:0}
    expanded=set()
    while heap:
        _,cost,node=heapq.heappop(heap)
        if node in expanded or cost!=best[node]:continue
        expanded.add(node)
        if len(expanded)>MAX_EXPANSIONS:raise RuntimeError("Search bound exceeded")
        if node==GOAL:
            return {"cost":cost,"expansions":len(expanded),"solved":True}
        x,y=node
        for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if not (0<=nx<GRID_SIZE and 0<=ny<GRID_SIZE):continue
            step=grid[ny][nx]
            if step is None:continue
            neighbor=(nx,ny)
            new=cost+step
            if new<best.get(neighbor,float("inf")):
                best[neighbor]=new
                heapq.heappush(heap,(new+h(neighbor),new,neighbor))
    return {"cost":None,"expansions":len(expanded),"solved":False}

def benchmark(variant,seeds):
    if variant not in CANDIDATES:raise ValueError("Unauthorized proposal")
    results=[]
    for seed in seeds:
        grid=make_grid(seed)
        target=search(grid,"dijkstra")
        observed=search(grid,variant)
        results.append({"seed":seed,"optimal_cost":target["cost"],
                        "cost":observed["cost"],"expansions":observed["expansions"],
                        "optimal":target["solved"] and observed["solved"] and
                                  target["cost"]==observed["cost"]})
    return {
      "cases":len(results),"optimal_cases":sum(r["optimal"] for r in results),
      "avg_expansions":round(sum(r["expansions"] for r in results)/len(results),3),
      "digest":checksum(results)
    }

def select(dev):
    """Require exact optimality on every development case, then minimize expansions."""
    allowed=[k for k in CANDIDATES if dev[k]["optimal_cases"]==dev[k]["cases"]]
    if not allowed:raise RuntimeError("No optimal candidate")
    return min(allowed,key=lambda k:(dev[k]["avg_expansions"],CANDIDATES.index(k)))

def run():
    # SOLO: one deterministic worker proposes, executes, selects.
    solo_dev={k:benchmark(k,SEEDS_DEV) for k in CANDIDATES}
    solo_selected=select(solo_dev)
    solo_plan={"candidates":CANDIDATES,"dev_seed_sha":checksum(SEEDS_DEV),
               "budget_development_searches":len(CANDIDATES)*len(SEEDS_DEV)}
    # TEAM: planner, engineer and independent evaluator exchange receipts.
    planner={"protocol":PROTOCOL,"plan":solo_plan,
             "role":"planner","proposal_is_ai_generated":False}
    planner_sha=checksum(planner)
    engineered={"plan_sha":planner_sha,"dev":{k:benchmark(k,SEEDS_DEV)
                    for k in CANDIDATES}}
    engineer_sha=checksum(engineered)
    reviewed_dev={k:benchmark(k,SEEDS_DEV) for k in CANDIDATES}
    if reviewed_dev!=engineered["dev"]:raise RuntimeError("Independent recomputation failed")
    team_selected=select(reviewed_dev)
    reviewed={"engineer_sha":engineer_sha,"recomputed":True,
              "selection":team_selected,"reviewer_is_ai":False}
    # Same holdout and same number of candidate runs per arm; evaluator does
    # extra development work, reported explicitly rather than hiding overhead.
    solo_holdout=benchmark(solo_selected,SEEDS_TEST)
    team_holdout=benchmark(team_selected,SEEDS_TEST)
    return {
      "protocol":PROTOCOL,
      "task":"weighted_grid_shortest_path_with_optimality_oracle",
      "development_cases":len(SEEDS_DEV),"test_cases":len(SEEDS_TEST),
      "seed_overlap":bool(set(SEEDS_DEV)&set(SEEDS_TEST)),
      "seed_set_digests":{"development":checksum(SEEDS_DEV),"test":checksum(SEEDS_TEST)},
      "common_budget":{"candidate_count":len(CANDIDATES),
                       "max_expansions_per_search":MAX_EXPANSIONS,
                       "development_candidate_evaluations":len(CANDIDATES)*len(SEEDS_DEV),
                       "holdout_candidate_evaluations":len(SEEDS_TEST)},
      "solo":{"selected":solo_selected,"development":solo_dev,"holdout":solo_holdout,
              "stages":1},
      "team":{"selected":team_selected,"development":engineered["dev"],
              "holdout":team_holdout,"stages":3,
              "planner_sha":planner_sha,"engineer_sha":engineer_sha,
              "recomputed_dev":reviewed["recomputed"],
              "extra_development_verification_evaluations":len(CANDIDATES)*len(SEEDS_DEV)},
      "same_selection":solo_selected==team_selected,
      "same_holdout_metrics":solo_holdout==team_holdout,
      "real_ai_agents":0,"external_dataset":False,
      "protected_unseen_external_holdout":False,
      "promotion_approved":False,"production_changes":False,
      "limitations":[
          "Both arms are deterministic algorithms, not AI-backed agents",
          "Candidate proposals are identical and hand-coded, not independently generated",
          "Synthetic heldout test seeds are reproducible but not externally independent",
          "Model improvement and recursion are not demonstrated",
          "Team incurs additional 72 development re-evaluations; comparison is not equal total compute"
      ]
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    report=run()
    blob=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if args.output:
        if args.output.is_symlink() or not args.output.parent.is_dir():raise ValueError("Invalid output path")
        args.output.write_text(blob,encoding="utf8")
    print(blob,end="")

if __name__=="__main__":main()
