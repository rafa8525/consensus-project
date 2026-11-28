"""M23 preregistered small symbolic-rule inference benchmark (offline only).

This evaluates deterministic allowlisted program synthesis on generated examples.
No LLM agents, model weights, self-modifying code, or external services.
"""
import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

MOD=11
FAMILIES=("affine","square","interaction")
POLICIES=("majority","affine_search","three_family_search")
DEV_SEEDS={f:tuple(range(81000+1000*i,81012+1000*i)) for i,f in enumerate(FAMILIES)}
TEST_SEEDS={f:tuple(range(91000+1000*i,91020+1000*i)) for i,f in enumerate(FAMILIES)}
MAX_HYPOTHESES=4000

def hash_obj(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def features(family,x,z):
    if family=="affine":return x,z
    if family=="square":return x*x,z
    if family=="interaction":return x*z,z
    raise ValueError("Unknown family")

def calculate(family,a,b,c,x,z):
    v,w=features(family,x,z)
    return (a*v+b*w+c)%MOD

def make_task(family,seed):
    if family not in FAMILIES or seed not in DEV_SEEDS[family]+TEST_SEEDS[family]:
        raise ValueError("Unsupported task")
    rng=random.Random(seed+100000*FAMILIES.index(family))
    a,b=rng.randint(1,10),rng.randint(1,10)
    c=rng.randrange(MOD)
    pairs=[(x,z) for x in range(MOD) for z in range(MOD)]
    rng.shuffle(pairs)
    observed=[(x,z,calculate(family,a,b,c,x,z)) for x,z in pairs[:8]]
    withheld=[(x,z,calculate(family,a,b,c,x,z)) for x,z in pairs[8:24]]
    return observed,withheld

def majority(demos):
    counts=Counter(y for _,_,y in demos)
    return min(counts,key=lambda y:(-counts[y],y))

def discover(demos,policy):
    if policy not in POLICIES:raise ValueError("Unapproved program policy")
    if len(demos)!=8 or len({(x,z) for x,z,_ in demos})!=8:
        raise ValueError("Malformed demonstrations")
    if any(type(v) is not int or not 0<=v<MOD for row in demos for v in row):
        raise ValueError("Invalid modular symbols")
    default=majority(demos)
    if policy=="majority":return None,0,default
    allowed=("affine",) if policy=="affine_search" else FAMILIES
    attempts=0
    # Only evaluate program candidates in fixed allowlisted, preregistered DSL.
    for family in allowed:
        for a in range(1,MOD):
            for b in range(1,MOD):
                for c in range(MOD):
                    attempts+=1
                    if attempts>MAX_HYPOTHESES:raise RuntimeError("Hypothesis budget exceeded")
                    if all(calculate(family,a,b,c,x,z)==target for x,z,target in demos):
                        return (family,a,b,c),attempts,default
    return None,attempts,default

def run_one(policy,observed,queries):
    program,attempts,fallback=discover(observed,policy)
    predictions=[calculate(*program,x,z) if program else fallback for x,z,_ in queries]
    return {"predictions":predictions,"hypotheses_evaluated":attempts,
            "rule_found":program is not None}

def collect(seeds):
    results={}
    for policy in POLICIES:
        details=[]
        for family in FAMILIES:
            for seed in seeds[family]:
                demos,holdout=make_task(family,seed)
                observation=run_one(policy,demos,holdout)
                actual=[y for _,_,y in holdout]
                correct=sum(a==b for a,b in zip(observation["predictions"],actual))
                details.append({"family":family,"seed":seed,"correct":correct,
                                "total":len(actual),
                                "work":observation["hypotheses_evaluated"],
                                "found":observation["rule_found"]})
        per_family={}
        for family in FAMILIES:
            rows=[r for r in details if r["family"]==family]
            per_family[family]={"correct":sum(r["correct"] for r in rows),
                                "total":sum(r["total"] for r in rows),
                                "rules_found":sum(r["found"] for r in rows),
                                "work":sum(r["work"] for r in rows)}
        results[policy]={
            "per_family":per_family,
            "correct":sum(r["correct"] for r in details),
            "total":sum(r["total"] for r in details),
            "total_hypotheses":sum(r["work"] for r in details),
            "sha256":hash_obj(details)}
    return results

def choose(dev):
    # Selection only sees development examples; never the test set.
    return min(POLICIES,key=lambda p:(-dev[p]["correct"],dev[p]["total_hypotheses"],
                                      POLICIES.index(p)))

def execute():
    development=collect(DEV_SEEDS)
    selected=choose(development)
    # Test measurements are all collected after selecting, for transparent
    # comparison; they are not used to change the selected policy.
    evaluation=collect(TEST_SEEDS)
    output={"protocol":"m23_symbolic_rule_induction_v1",
        "task":"infer_modular_program_from_eight_examples",
        "families":list(FAMILIES),"policies":list(POLICIES),
        "development_tasks":sum(len(v) for v in DEV_SEEDS.values()),
        "evaluation_tasks":sum(len(v) for v in TEST_SEEDS.values()),
        "withheld_predictions_per_evaluation_task":16,
        "development":development,"selected":selected,"test":evaluation,
        "development_seed_sha256":hash_obj(DEV_SEEDS),
        "evaluation_seed_sha256":hash_obj(TEST_SEEDS),
        "test_exposed_after_first_run":True,"external_benchmark":False,
        "selection_uses_test":False,"max_hypotheses_per_task":MAX_HYPOTHESES,
        "live_model_calls":0,"ai_agents":0,"model_weights_trained":False,
        "production_changes":False,"promotion_approved":False}
    if any(set(DEV_SEEDS[f])&set(TEST_SEEDS[f]) for f in FAMILIES):
        raise ValueError("Seed overlap")
    return output

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    data=json.dumps(execute(),sort_keys=True,indent=2)+"\n"
    if a.output:
        if a.output.is_symlink() or not a.output.parent.is_dir():
            raise ValueError("Unsafe output")
        a.output.write_text(data,encoding="utf8")
    print(data,end="")

if __name__=="__main__":main()
