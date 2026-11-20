"""Bounded three-role experiment pipeline using durable SQLite receipts.

Three genuinely executing deterministic *software roles*, NOT three LLM agents.
No production writes, external APIs, model promotion, or online autonomy.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from local_inference import TRAIN, fit as fit_word, predict as predict_word
from model_improvement_experiment import VALIDATION, train_char, predict_char
from replicated_model_evaluation import CONFIRMATION, macro_f1

ROLES = ("research_planner", "model_engineer", "independent_evaluator")
VERSION = "3-role-research-v1"

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"))

def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf8")).hexdigest()

def connect(db):
    db=Path(db)
    if db.is_symlink() or not db.parent.is_dir():
        raise ValueError("Untrusted database path")
    c=sqlite3.connect(str(db),timeout=10,isolation_level=None)
    c.execute("PRAGMA busy_timeout=10000")
    c.execute("PRAGMA journal_mode=WAL")
    c.executescript("""CREATE TABLE IF NOT EXISTS task_receipts(
        role TEXT PRIMARY KEY, input_sha TEXT NOT NULL,
        output_json TEXT NOT NULL, output_sha TEXT NOT NULL,
        completed_utc TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS workflow_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);""")
    return c

def _get(c,role):
    row=c.execute("SELECT input_sha,output_json,output_sha FROM task_receipts WHERE role=?",(role,)).fetchone()
    if row is None:return None
    obj=json.loads(row[1])
    if digest(obj)!=row[2]:raise ValueError("Stored receipt hash mismatch")
    return {"input_sha":row[0],"output":obj,"sha":row[2]}

def _write_once(c,role,input_sha,output):
    from datetime import datetime,timezone
    if role not in ROLES:raise ValueError("Unsupported role")
    output_sha=digest(output)
    c.execute("BEGIN IMMEDIATE")
    try:
        old=_get(c,role)
        if old is not None:
            if old["input_sha"]!=input_sha or old["sha"]!=output_sha:
                raise ValueError("Immutable receipt conflict")
            c.execute("COMMIT")
            return old
        earlier=ROLES[:ROLES.index(role)]
        if any(_get(c,r) is None for r in earlier):
            raise ValueError("Missing upstream receipt")
        c.execute("INSERT INTO task_receipts VALUES(?,?,?,?,?)",
                  (role,input_sha,canonical(output),output_sha,
                   datetime.now(timezone.utc).isoformat()))
        c.execute("COMMIT")
    except BaseException:
        c.execute("ROLLBACK")
        raise
    return _get(c,role)

def plan():
    # Bounded choices only; does not call an LLM or invent arbitrary architectures.
    options=[{"kind":"word_nb"},{"kind":"word_char_nb","n":3,"alpha":0.5},
             {"kind":"word_char_nb","n":4,"alpha":1.0}]
    return {"version":VERSION,"hypothesis":"Character n-grams increase task classification validation macro F1",
            "alternatives":options,"development_sha":digest({"train":TRAIN,"validation":VALIDATION}),
            "budget":{"max_model_fits":3,"max_examples":30},
            "selection":"validation_macro_f1","retest_used_for_selection":False,
            "production_changes":False}

def predict_for(model_spec,text,models):
    key=canonical(model_spec)
    obj=models[key]
    if model_spec["kind"]=="word_nb":
        return predict_word(obj,text)["label"]
    return predict_char(obj,text)

def evaluate_rows(rows,predictor):
    truth=[a for a,_ in rows]
    predictions=[predictor(t) for _,t in rows]
    return {"correct":sum(a==b for a,b in zip(truth,predictions)),
            "count":len(rows),
            "macro_f1":round(macro_f1(truth,predictions),6)}

def build_models(alternatives):
    if len(alternatives)>3:raise ValueError("Model budget exceeded")
    models={}
    for spec in alternatives:
        if spec=={"kind":"word_nb"}:
            model=fit_word(TRAIN)
        elif spec in ({"kind":"word_char_nb","n":3,"alpha":0.5},
                      {"kind":"word_char_nb","n":4,"alpha":1.0}):
            model=train_char(TRAIN,n=spec["n"],alpha=spec["alpha"])
        else:raise ValueError("Unapproved architecture choice")
        models[canonical(spec)]=model
    return models

def engineer(plan_receipt):
    p=plan_receipt["output"]
    if p["development_sha"]!=digest({"train":TRAIN,"validation":VALIDATION}):
        raise ValueError("Development data changed")
    if p["budget"]["max_model_fits"]!=3 or len(p["alternatives"])!=3:
        raise ValueError("Plan budget mismatch")
    models=build_models(p["alternatives"])
    outcomes=[]
    for spec in p["alternatives"]:
        metrics=evaluate_rows(VALIDATION,lambda text:predict_for(spec,text,models))
        outcomes.append({"spec":spec,"validation":metrics})
    # Baseline wins ties. New candidate must strictly beat it.
    baseline=outcomes[0]
    alternatives=[o for o in outcomes[1:] if o["validation"]["macro_f1"]>
                  baseline["validation"]["macro_f1"]]
    chosen=max(alternatives,key=lambda x:(x["validation"]["macro_f1"],
               -p["alternatives"].index(x["spec"]))) if alternatives else baseline
    return {"plan_receipt_sha":plan_receipt["sha"],
            "outcomes":outcomes,"selected":chosen["spec"],
            "selected_validation":chosen["validation"],
            "selection_uses_validation_only":True,
            "test_evaluated":False,"production_changes":False}

def independent_review(plan_receipt,engineer_receipt):
    p=plan_receipt["output"]
    output=engineer_receipt["output"]
    if output["plan_receipt_sha"]!=plan_receipt["sha"]:
        raise ValueError("Plan handoff modified")
    specs=p["alternatives"]
    models=build_models(specs)
    recomputed=[{"spec":spec,"validation":evaluate_rows(
        VALIDATION,lambda text:predict_for(spec,text,models))} for spec in specs]
    if recomputed!=output["outcomes"]:raise ValueError("Engineer metrics not reproducible")
    baseline=recomputed[0]
    eligible=[x for x in recomputed[1:] if x["validation"]["macro_f1"]>
              baseline["validation"]["macro_f1"]]
    selected=max(eligible,key=lambda x:(x["validation"]["macro_f1"],
               -specs.index(x["spec"])))["spec"] if eligible else baseline["spec"]
    if selected!=output["selected"]:raise ValueError("Unverified model selection")
    exposed=evaluate_rows(CONFIRMATION,lambda text:predict_for(selected,text,models))
    exposed_baseline=evaluate_rows(CONFIRMATION,
         lambda text:predict_for(specs[0],text,models))
    return {"engineer_receipt_sha":engineer_receipt["sha"],
            "plan_receipt_sha":plan_receipt["sha"],
            "recomputed_validation_matches":True,
            "selected":selected,
            "already_exposed_confirmation":{"selected":exposed,"baseline":exposed_baseline},
            "independent_holdout_achieved":False,
            "research_candidate_approved":False,
            "production_changes":False,
            "review_findings":["Validation was used to select alternatives",
                 "Confirmation data already exposed in prior milestones",
                 "Small hand-authored corpus cannot establish generalization",
                 "This is a bounded deterministic three-role pipeline, not independent AI agents"]}

def step(con,role):
    if role not in ROLES:raise ValueError("Unauthorized role")
    planner=_get(con,ROLES[0])
    engineering=_get(con,ROLES[1])
    if role==ROLES[0]:
        result=plan()
        input_sha=digest({"version":VERSION,"role":role})
    elif role==ROLES[1]:
        if planner is None:raise ValueError("Planner not completed")
        result=engineer(planner)
        input_sha=planner["sha"]
    else:
        if planner is None or engineering is None:raise ValueError("Upstream task incomplete")
        result=independent_review(planner,engineering)
        input_sha=digest([planner["sha"],engineering["sha"]])
    return _write_once(con,role,input_sha,result)

def snapshot(con):
    rows=[]
    for role in ROLES:
        receipt=_get(con,role)
        rows.append({"role":role,"status":"completed" if receipt else "pending",
                     "sha256":receipt["sha"] if receipt else None,
                     "result":receipt["output"] if receipt else None})
    return {"version":VERSION,"roles":rows,"fully_completed":all(
        row["status"]=="completed" for row in rows),
        "deployment_approved":False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",type=Path,required=True)
    parser.add_argument("command",choices=("init","planner","engineer","evaluator","status","run"))
    args=parser.parse_args()
    con=connect(args.db)
    try:
        if args.command=="run":
            for role in ROLES:step(con,role)
        elif args.command in ("planner","engineer","evaluator"):
            step(con,{"planner":ROLES[0],"engineer":ROLES[1],
                     "evaluator":ROLES[2]}[args.command])
        print(json.dumps(snapshot(con),sort_keys=True,indent=2))
    finally:con.close()

if __name__=="__main__": main()
