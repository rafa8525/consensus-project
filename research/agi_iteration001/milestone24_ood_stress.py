"""M24 preregistered out-of-language stress test for frozen M23 synthesizer."""
import argparse
import json
import random
from pathlib import Path
from milestone23_symbolic_benchmark import MOD,discover,calculate,majority,hash_obj

KINDS=("affine","square","interaction","mixed","conditional")
IN_KINDS=KINDS[:3]
OOD_KINDS=KINDS[3:]
SEEDS={name:tuple(range(start,start+(10 if name in IN_KINDS else 15)))
       for name,start in zip(KINDS,(110000,111000,112000,120000,121000))}

def hidden(kind,a,b,c,x,z):
    if kind in IN_KINDS:return calculate(kind,a,b,c,x,z)
    if kind=="mixed":return (a*x*x+b*x*z+c)%MOD
    if kind=="conditional":return (a*x+b*z+c+3*(x>=5))%MOD
    raise ValueError("Unsupported generator rule")

def task(kind,seed):
    if kind not in KINDS or type(seed) is not int or seed not in SEEDS[kind]:
        raise ValueError("Unregistered test")
    rng=random.Random(seed+1000*KINDS.index(kind))
    a=rng.randint(1,10)
    b=rng.randint(1,10)
    c=rng.randrange(MOD)
    pairs=[(x,z) for x in range(MOD) for z in range(MOD)]
    rng.shuffle(pairs)
    points=[(x,z,hidden(kind,a,b,c,x,z)) for x,z in pairs[:24]]
    return points[:8],points[8:]

def one(kind,seed):
    demos,queries=task(kind,seed)
    program,work,fallback=discover(demos,"three_family_search")
    accepted=program is not None
    guesses=[calculate(*program,x,z) if accepted else None for x,z,_ in queries]
    forced=[x if x is not None else fallback for x in guesses]
    truth=[label for _,_,label in queries]
    return {
      "family":kind,"seed":seed,"in_language":kind in IN_KINDS,
      "accepted":accepted,"work":work,
      "correct_accepted":sum(g==t for g,t in zip(guesses,truth)),
      "correct_forced":sum(g==t for g,t in zip(forced,truth)),
      "queries":len(truth)
    }

def execute():
    rows=[one(k,seed) for k in KINDS for seed in SEEDS[k]]
    summaries={}
    for kind in KINDS:
        subset=[r for r in rows if r["family"]==kind]
        summaries[kind]={
          "tasks":len(subset),
          "accepted":sum(r["accepted"] for r in subset),
          "abstained":sum(not r["accepted"] for r in subset),
          "correct_abstention_counted_wrong":sum(r["correct_accepted"] for r in subset),
          "correct_forced_fallback":sum(r["correct_forced"] for r in subset),
          "total_queries":sum(r["queries"] for r in subset),
          "program_hypotheses_tested":sum(r["work"] for r in subset),
        }
    def combined(kinds):
        subset=[r for r in rows if r["family"] in kinds]
        return {"tasks":len(subset),"accepted":sum(r["accepted"] for r in subset),
                "correct_on_all_queries_with_abstention_counted_wrong":
                  sum(r["correct_accepted"] for r in subset),
                "correct_forced_fallback":sum(r["correct_forced"] for r in subset),
                "total_queries":sum(r["queries"] for r in subset)}
    in_domain=combined(IN_KINDS)
    ood=combined(OOD_KINDS)
    return {
      "protocol":"m24_frozen_symbolic_ood_stress_v1",
      "preregistration_file":"MILESTONE_24_PREREGISTRATION.md",
      "in_domain":in_domain,"out_of_domain":ood,
      "per_family":summaries,
      "seed_sha256":hash_obj(SEEDS),"evidence_sha256":hash_obj(rows),
      "frozen_m23_search":True,"abstains_on_no_consistent_program":True,
      "live_model_calls":0,"externally_sourced":False,"model_training":False,
      "production_changes":False,"promotion_approved":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    blob=json.dumps(execute(),sort_keys=True,indent=2)+"\n"
    if a.output:
        if a.output.is_symlink() or not a.output.parent.is_dir():
            raise ValueError("Unsafe output")
        a.output.write_text(blob,encoding="utf8")
    print(blob,end="")
if __name__=="__main__":main()
