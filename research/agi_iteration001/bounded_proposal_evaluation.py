"""Offline Milestone 25: bounded evaluation of the *approved proposal contract*.

Uses a separately validated, FIXED LOCAL fixture, not unretained live API prose.
Exactly three training fits on 18 hand-authored samples; evaluates 12
hand-authored validation samples; never touches holdout TEST or production.
No networking, credentials, paid requests, persistence or automatic promotion.
"""
from __future__ import annotations
import hashlib
import json
from local_inference import TRAIN, LABELS, fit as fit_word, predict as predict_word
from model_improvement_experiment import VALIDATION, train_char, predict_char
from proposal_provider import (
    OfflineProposalProvider, validate_proposal, MODEL_CATALOG, DATASET_IDS, BUDGET
)
from replicated_model_evaluation import macro_f1

def _check_data(train, validation):
    if len(train) > BUDGET["max_examples"]:
        raise ValueError("Training examples exceed proposal budget")
    if len(train) != 18 or len(validation) != 12:
        raise ValueError("Unexpected fixed offline dataset sizes")
    if not train or not validation:
        raise ValueError("Empty research split")
    train_text={x.lower().strip() for _,x in train}
    val_text={x.lower().strip() for _,x in validation}
    if len(train_text)!=len(train) or len(val_text)!=len(validation) or train_text & val_text:
        raise ValueError("Duplicate text or train-validation leakage")
    for row in list(train)+list(validation):
        if not isinstance(row,tuple) or len(row)!=2 or row[0] not in LABELS or not isinstance(row[1],str):
            raise ValueError("Invalid fixed research row")

def evaluate(proposal=None):
    """Only the fixed approved model catalog can execute; cap all fits to three."""
    if proposal is None:
        proposal=OfflineProposalProvider().propose()
    validated=validate_proposal(proposal)
    if validated["alternatives"]!=list(MODEL_CATALOG) or validated["dataset_ids"]!=list(DATASET_IDS):
        raise ValueError("Unapproved evaluation contract")
    if validated["compute_budget"]!=BUDGET or validated["metric"]!="validation_macro_f1":
        raise ValueError("Unapproved resource or metric")
    training=tuple(TRAIN)
    validation=tuple(VALIDATION)
    _check_data(training,validation)
    actual=[y for y,_ in validation]
    results=[]
    fits=0
    for spec in validated["alternatives"]:
        if fits>=BUDGET["max_model_fits"]:
            raise ValueError("Training fit budget reached")
        if spec["kind"]=="word_nb":
            model=fit_word(training)
            predict=lambda text:predict_word(model,text)["label"]
        elif spec["kind"]=="word_char_nb":
            model=train_char(training,n=spec["n"],alpha=spec["alpha"])
            predict=lambda text:predict_char(model,text)
        else:
            raise ValueError("Unknown candidate")
        fits+=1
        labels=[predict(text) for _,text in validation]
        correct=sum(y==p for y,p in zip(actual,labels))
        results.append({
            "model":dict(spec),
            "validation_correct":correct,
            "validation_total":len(actual),
            "validation_macro_f1":round(macro_f1(actual,labels),6)
        })
    base=results[0]["validation_macro_f1"]
    ordered=sorted(range(len(results)),key=lambda i:(-results[i]["validation_macro_f1"],i))
    selected=ordered[0]
    digest=hashlib.sha256(json.dumps({"train":training,"validation":validation},
                   sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {
        "milestone":"bounded_offline_proposal_evaluation_v1",
        "proposal_origin":"fixed_offline_fixture_not_recovered_live_output",
        "dataset_origin":"hand_authored_internal_not_external",
        "dataset_sha256":digest,
        "split_sizes":{"train":len(training),"validation":len(validation)},
        "holdout_accessed":False,
        "fit_count":fits,
        "max_model_fits":BUDGET["max_model_fits"],
        "metric":"validation_macro_f1",
        "evaluations":results,
        "selected_index_by_validation":selected,
        "selected_validation_gain":round(results[selected]["validation_macro_f1"]-base,6),
        "independent_generalization_verified":False,
        "promotion_approved":False,
        "production_changes":False,
        "api_calls":0,
        "limitations":[
           "Hand-authored samples, not independent external data",
           "Validation-only selection; no confirmation/holdout used in this milestone",
           "Live API proposal hypothesis text was not retained; fixed safe proposal fixture is used",
           "Validation gains do not establish external generalization or AGI"
        ],
    }

if __name__=="__main__":
    print(json.dumps(evaluate(),sort_keys=True,indent=2))
