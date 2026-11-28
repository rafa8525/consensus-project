"""Milestone 20: AI-authored, typed search proposals on fresh synthetic planning tasks.

The proposals are authored for this research experiment, not produced by a
running autonomous model agent. Never exec model text or trust outcome claims.
"""
import argparse
import hashlib
import heapq
import json
from pathlib import Path
from solo_vs_team_planning import make_grid, GRID_SIZE, GOAL, START

DEV_SEEDS=tuple(range(20000,20032))
TEST_SEEDS=tuple(range(30000,30064))
EXPOSED_SEEDS=set(range(1000,1024))|set(range(9000,9064))
CANDIDATE_LIMIT=3
VALID_MODES=("dijkstra","manhattan","min_edge_manhattan")
VALID_TIES=("low_g","high_g")
ALLOW_WEIGHT=(1.0,1.25,1.5)
PROTOCOL="bounded_ai_authored_planning_v1"

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"))

def sha(obj):
    return hashlib.sha256(canonical(obj).encode("utf8")).hexdigest()

def validate(raw):
    if isinstance(raw,str):
        if len(raw.encode("utf8"))>4096:raise ValueError("Oversize proposal")
        raw=json.loads(raw)
    if not isinstance(raw,dict) or set(raw)!={"experiment_id","candidates","goal"}:
        raise ValueError("Unknown fields")
    if raw["experiment_id"]!="m20-planning-v1" or raw["goal"]!="optimal_then_fewer_expansions":
        raise ValueError("Wrong research goal")
    specs=raw["candidates"]
    if not isinstance(specs,list) or len(specs)!=CANDIDATE_LIMIT:
        raise ValueError("Exactly three bounded candidates required")
    seen=set()
    result=[]
    for row in specs:
        if not isinstance(row,dict) or set(row)!={"id","heuristic","weight","tie_break"}:
            raise ValueError("Unknown code fields")
        name,mode,weight,tie=(row[k] for k in ("id","heuristic","weight","tie_break"))
        if not isinstance(name,str) or name not in ("baseline","candidate_a","candidate_b"):
            raise ValueError("Unrecognized ID")
        if mode not in VALID_MODES or tie not in VALID_TIES or type(weight) not in (int,float) or weight not in ALLOW_WEIGHT:
            raise ValueError("Unapproved search parameters")
        if mode=="dijkstra" and weight!=1.0:
            raise ValueError("Dijkstra cannot be weighted")
        if name in seen:raise ValueError("Duplicate candidate ID")
        seen.add(name)
        result.append(dict(row))
    if [x["id"] for x in result]!=["baseline","candidate_a","candidate_b"]:
        raise ValueError("Candidate order invalid")
    if result[0]!={"id":"baseline","heuristic":"dijkstra","weight":1.0,"tie_break":"low_g"}:
        raise ValueError("Baseline must be preserved")
    if len({(x["heuristic"],x["weight"],x["tie_break"]) for x in result})!=3:
        raise ValueError("Duplicate strategies")
    return {"experiment_id":raw["experiment_id"],"goal":raw["goal"],"candidates":result}

class RecordedProposalProvider:
    """Simulates proposal file intake. Not a live LLM agent or API provider."""
    is_live_model=False
    def propose(self):
        return {"experiment_id":"m20-planning-v1",
                "goal":"optimal_then_fewer_expansions",
                "candidates":[
                    {"id":"baseline","heuristic":"dijkstra","weight":1.0,"tie_break":"low_g"},
                    {"id":"candidate_a","heuristic":"min_edge_manhattan","weight":1.0,"tie_break":"high_g"},
                    {"id":"candidate_b","heuristic":"min_edge_manhattan","weight":1.25,"tie_break":"high_g"}
                ]}

def bounded_search(grid,spec):
    """A* on positive weighted grid. Return exact path cost and expansion count."""
    size=GRID_SIZE
    if len(grid)!=size or any(len(r)!=size for r in grid):raise ValueError("Grid mismatch")
    if grid[0][0] is None or grid[-1][-1] is None:raise ValueError("Blocked end")
    min_step=min(x for row in grid for x in row if x is not None)
    def heuristic(p):
        distance=abs(GOAL[0]-p[0])+abs(GOAL[1]-p[1])
        if spec["heuristic"]=="dijkstra":return 0.
        if spec["heuristic"]=="manhattan":return spec["weight"]*distance
        return spec["weight"]*distance*min_step
    tie_high=spec["tie_break"]=="high_g"
    frontier=[(heuristic(START),0,0,START)]
    best={START:0}
    visited=set()
    count=0
    while frontier:
        _,_,cost,p=heapq.heappop(frontier)
        if cost!=best[p] or p in visited:continue
        visited.add(p)
        count+=1
        if count>GRID_SIZE*GRID_SIZE:raise RuntimeError("Expansion cap exceeded")
        if p==GOAL:return {"cost":cost,"expansions":count}
        x,y=p
        for nxt in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            a,b=nxt
            if not (0<=a<size and 0<=b<size):continue
            step=grid[b][a]
            if step is None or nxt in visited:continue
            new=cost+step
            if new<best.get(nxt,float("inf")):
                best[nxt]=new
                heapq.heappush(frontier,(new+heuristic(nxt),-new if tie_high else new,new,nxt))
    return {"cost":None,"expansions":count}

def score(spec,seeds):
    baseline={"id":"baseline","heuristic":"dijkstra","weight":1.0,"tie_break":"low_g"}
    observations=[]
    for seed in seeds:
        grid=make_grid(seed)
        expected=bounded_search(grid,baseline)
        found=bounded_search(grid,spec)
        observations.append({"seed":seed,"optimal":found["cost"]==expected["cost"] and found["cost"] is not None,
                             "expansions":found["expansions"],"cost":found["cost"]})
    return {"cases":len(observations),"optimal_cases":sum(r["optimal"] for r in observations),
            "average_expansions":round(sum(r["expansions"] for r in observations)/len(observations),3),
            "sha256":sha(observations)}

def choose(specs,results):
    eligible=[s for s in specs if results[s["id"]]["optimal_cases"]==results[s["id"]]["cases"]]
    if not eligible:raise RuntimeError("All proposals failed optimality")
    return min(eligible,key=lambda s:(results[s["id"]]["average_expansions"],
                                     specs.index(s)))["id"]

def run(provider=None):
    provider=provider if provider is not None else RecordedProposalProvider()
    if getattr(provider,"is_live_model",True) is not False:raise PermissionError("Live providers disabled")
    proposals=validate(provider.propose())
    if set(DEV_SEEDS)&set(TEST_SEEDS) or (set(DEV_SEEDS)|set(TEST_SEEDS))&EXPOSED_SEEDS:
        raise ValueError("Seed leakage")
    dev={s["id"]:score(s,DEV_SEEDS) for s in proposals["candidates"]}
    selected=choose(proposals["candidates"],dev)
    selected_spec=next(s for s in proposals["candidates"] if s["id"]==selected)
    baseline_spec=proposals["candidates"][0]
    # Heldout is only accessed after model selection, and then becomes exposed.
    holdout_baseline=score(baseline_spec,TEST_SEEDS)
    holdout_selected=score(selected_spec,TEST_SEEDS)
    # Independent recomputation with same deterministic primitives is
    # arithmetic verification, not independently written evaluation software.
    verified=(dev=={s["id"]:score(s,DEV_SEEDS) for s in proposals["candidates"]})
    return {"protocol":PROTOCOL,"source":"ai_assistant_authored_recorded_proposal_not_live",
            "proposal_sha256":sha(proposals),"candidate_count":len(proposals["candidates"]),
            "development_seeds_sha256":sha(DEV_SEEDS),"holdout_seeds_sha256":sha(TEST_SEEDS),
            "development_cases":len(DEV_SEEDS),"test_cases":len(TEST_SEEDS),
            "development_candidate_evaluations":len(DEV_SEEDS)*len(proposals["candidates"]),
            "development":dev,"selection":selected,
            "test_baseline":holdout_baseline,"test_selected":holdout_selected,
            "development_recomputed":verified,
            "holdout_is_now_exposed":True,"externally_independent_test":False,
            "live_model_calls":0,"cost_usd":0,"model_training_performed":False,
            "production_changes":False,"promotion_approved":False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    a=parser.parse_args()
    result=run()
    blob=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.output:
        if a.output.is_symlink() or not a.output.parent.is_dir():raise ValueError("Unsafe result path")
        a.output.write_text(blob,encoding="utf8")
    print(blob,end="")
if __name__=="__main__":main()
