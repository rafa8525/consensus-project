"""Milestone 22: preregistered frozen A* admissibility and efficiency trial.

This compares two PRESELECTED deterministic algorithms; it is not a model-backed
researcher, external sealed benchmark or a demonstration of AGI.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from pathlib import Path

from milestone20_planner import bounded_search, sha
from milestone21_robustness import oracle_relaxation
from solo_vs_team_planning import GRID_SIZE

FAMILIES=("zigzag_corridor","concentric_costs","lane_barriers","bimodal_sparse")
SEEDS=tuple(range(73000,73048))
BASELINE={"id":"baseline","heuristic":"dijkstra","weight":1.0,"tie_break":"low_g"}
CANDIDATE={"id":"candidate_a","heuristic":"min_edge_manhattan","weight":1.0,"tie_break":"high_g"}
PROTOCOL="m22_preregistered_cross_family_admissible_v1"
TIMING_REPEATS=3
EXPOSED=tuple(range(1000,1024))+tuple(range(9000,9064))+tuple(range(20000,20032))+tuple(range(30000,30064))+tuple(range(61000,61064))

def grid_for(family,seed):
    if family not in FAMILIES or type(seed) is not int or seed not in SEEDS:
        raise ValueError("Unregistered family or seed")
    rng=random.Random(seed+100000*FAMILIES.index(family))
    cells=[]
    for y in range(GRID_SIZE):
        row=[]
        for x in range(GRID_SIZE):
            if family=="zigzag_corridor":
                # Alternating wall columns with seed-dependent, permeable gaps.
                wall=(x in (2,5,8)) and y!=((seed//(x+1))%GRID_SIZE)
                step=rng.randint(1,5)
                blocked=wall
            elif family=="concentric_costs":
                ring=min(x,y,GRID_SIZE-1-x,GRID_SIZE-1-y)
                step=(10 if ring in (1,3) else 1)+rng.randint(0,2)
                blocked=rng.random()<0.05
            elif family=="lane_barriers":
                step=1 if y%3==0 else rng.randint(5,12)
                blocked=(y in (3,6,9) and x!=((seed+y)//3)%GRID_SIZE)
            else:
                step=1 if rng.random()<0.72 else 12
                blocked=rng.random()<0.09
            row.append(None if blocked else step)
        cells.append(row)
    # Guarantee at least one traversable path, without affecting all interior traps.
    for x in range(GRID_SIZE):
        if cells[0][x] is None:
            cells[0][x]=rng.randint(1,3)
    for y in range(GRID_SIZE):
        if cells[y][-1] is None:
            cells[y][-1]=rng.randint(1,3)
    return tuple(tuple(row) for row in cells)

def validate_specs(baseline,candidate):
    if baseline!=BASELINE or candidate!=CANDIDATE:
        raise PermissionError("Frozen M22 candidate or baseline modified")

def score(*, latency=True, baseline=None, candidate=None):
    baseline=BASELINE if baseline is None else baseline
    candidate=CANDIDATE if candidate is None else candidate
    validate_specs(baseline,candidate)
    if set(SEEDS)&set(EXPOSED):
        raise ValueError("Evaluation seed leakage")
    family_reports={}
    for family in FAMILIES:
        rows=[]
        timings={"baseline":[],"candidate":[]}
        for seed in SEEDS:
            grid=grid_for(family,seed)
            oracle=oracle_relaxation(grid)
            base=bounded_search(grid,baseline)
            improved=bounded_search(grid,candidate)
            rows.append({
              "seed":seed,"oracle":oracle,
              "baseline_cost":base["cost"],"candidate_cost":improved["cost"],
              "base_expansions":base["expansions"],"candidate_expansions":improved["expansions"],
              "baseline_correct":base["cost"]==oracle and oracle is not None,
              "candidate_correct":improved["cost"]==oracle and oracle is not None,
            })
            if latency:
                # Descriptive wall-clock measurement only; not a CI pass criterion.
                for repetition in range(TIMING_REPEATS):
                    ordered=(("baseline",baseline),("candidate",candidate))
                    if repetition%2:ordered=tuple(reversed(ordered))
                    for name,spec in ordered:
                        tick=time.perf_counter_ns()
                        measured=bounded_search(grid,spec)
                        elapsed=time.perf_counter_ns()-tick
                        if measured["cost"]!=(base if name=="baseline" else improved)["cost"]:
                            raise RuntimeError("Timing run disagreement")
                        timings[name].append(elapsed)
        cases=len(rows)
        base_total=sum(x["base_expansions"] for x in rows)
        candidate_total=sum(x["candidate_expansions"] for x in rows)
        failures=[{"seed":r["seed"],"actual":r["candidate_cost"],"oracle":r["oracle"]}
                  for r in rows if not r["candidate_correct"]]
        family_reports[family]={
          "cases":cases,
          "baseline_optimal":sum(x["baseline_correct"] for x in rows),
          "candidate_optimal":sum(x["candidate_correct"] for x in rows),
          "baseline_mean_expansions":round(base_total/cases,3),
          "candidate_mean_expansions":round(candidate_total/cases,3),
          "candidate_expansion_reduction_percent":round(100*(base_total-candidate_total)/base_total,3),
          "candidate_failures":failures[:5],
          "evidence_sha256":sha(rows),
          "latency_median_ns":{k:int(statistics.median(v)) for k,v in timings.items()} if latency else None
        }
    total=len(FAMILIES)*len(SEEDS)
    optimal=sum(f["candidate_optimal"] for f in family_reports.values())
    return {
      "protocol":PROTOCOL,"preregistration_file":"MILESTONE_22_PREREGISTRATION.md",
      "specs":{"baseline":baseline,"candidate":candidate},
      "cases":total,"families":family_reports,
      "optimal_candidate_total":optimal,"optimal_baseline_total":
        sum(f["baseline_optimal"] for f in family_reports.values()),
      "primary_correctness_pass":optimal==total,
      "latency_is_exploratory":True,
      "latency_repeats":TIMING_REPEATS if latency else 0,
      "external_protected_holdout":False,
      "holdout_now_exposed":True,
      "live_model_calls":0,"model_training":False,
      "production_changes":False,"promotion_approved":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    p.add_argument("--no-latency",action="store_true")
    a=p.parse_args()
    result=score(latency=not a.no_latency)
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.output:
        if a.output.is_symlink() or not a.output.parent.is_dir():
            raise ValueError("Unsafe output")
        a.output.write_text(text,encoding="utf8")
    print(text,end="")

if __name__=="__main__":main()
