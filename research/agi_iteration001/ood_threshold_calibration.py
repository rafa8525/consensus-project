"""Milestone 13: development-only OOD threshold calibration.

Uses CLINC150 oos_val, never oos_test. The domain mismatch remains a
proxy task; prior confirmation examples are already exposed, so are not a
fresh independent test. No model promotion.
"""
import argparse
import hashlib
import json
from pathlib import Path
from local_inference import TRAIN, LABELS, fit as fit_word, predict as predict_word
from model_improvement_experiment import VALIDATION, train_char, predict_char
from replicated_model_evaluation import CONFIRMATION
from clinc_ood_protocol import known_fraction

MAX_BYTES = 5_000_000
THRESHOLDS = tuple(i/20 for i in range(1,20))
# In-domain validation previously existed and may have influenced model design.
# Calibrate only the abstention gate, not the underlying classifier.
IN_DOMAIN_CALIBRATION = VALIDATION
EXPOSED_CONFIRMATION = CONFIRMATION

def read_oos_validation(path, expected_sha256):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>MAX_BYTES:
        raise ValueError("Missing, linked or oversized CLINC source")
    raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError("CLINC source checksum mismatch")
    obj=json.loads(raw.decode("utf8"))
    if not isinstance(obj,dict) or not isinstance(obj.get("oos_val"),list):
        raise ValueError("CLINC oos_val unavailable")
    if "oos_test" in obj and not isinstance(obj["oos_test"],list):
        raise ValueError("Malformed dataset structure")
    rows=obj["oos_val"]
    if len(rows)<50 or len(rows)>2000:
        raise ValueError("Unexpected validation size")
    texts=[]
    seen=set()
    for row in rows:
        if not isinstance(row,list) or len(row)!=2 or row[1]!="oos" or not isinstance(row[0],str):
            raise ValueError("Invalid validation row")
        txt=row[0].strip()
        if not 4<=len(txt)<=500:raise ValueError("Invalid query length")
        norm=" ".join(txt.lower().split())
        if norm not in seen:
            seen.add(norm)
            texts.append(txt)
    if len(texts)<50:raise ValueError("Insufficient distinct OOD cases")
    return texts

def threshold_metrics(good,scores,ood,threshold):
    if not good or not ood or len(good)!=len(scores):
        raise ValueError("Missing calibration observations")
    correct_accept=sum(bool(correct) and value>=threshold for correct,value in zip(good,scores))
    false_accept=sum(value>=threshold for value in ood)
    # Balanced objective: maximize in-domain correct-accept rate and OOD reject rate.
    in_success=correct_accept/len(good)
    ood_reject=1-false_accept/len(ood)
    objective=(in_success+ood_reject)/2
    return {"threshold":threshold,"in_domain_correct_accept":correct_accept,
            "in_domain_total":len(good),"ood_false_accept":false_accept,
            "ood_total":len(ood),"balanced_objective":round(objective,6)}

def choose_threshold(good,scores,ood):
    results=[threshold_metrics(good,scores,ood,threshold) for threshold in THRESHOLDS]
    # Deterministic tie break: prefer higher OOD rejection, then higher threshold.
    return max(results,key=lambda x:(x["balanced_objective"],
              -x["ood_false_accept"],x["threshold"]))

def calibrate(ood_queries):
    word_model=fit_word(TRAIN)
    char_model=train_char(TRAIN,n=3,alpha=0.5)
    summaries={}
    for kind,model,pred in (
        ("word",word_model,lambda text:predict_word(word_model,text)["label"]),
        ("char",char_model,lambda text:predict_char(char_model,text))):
        vocabulary=set(model["vocab"])
        good=[pred(text)==label for label,text in IN_DOMAIN_CALIBRATION]
        known=[known_fraction(text,vocabulary,kind) for _,text in IN_DOMAIN_CALIBRATION]
        ood=[known_fraction(text,vocabulary,kind) for text in ood_queries]
        best=choose_threshold(good,known,ood)
        # Already-exposed, hand-authored confirmation is descriptive only.
        confirmation_correct=[pred(text)==label for label,text in EXPOSED_CONFIRMATION]
        confirmation_scores=[known_fraction(text,vocabulary,kind) for _,text in EXPOSED_CONFIRMATION]
        accepted=sum(x>=best["threshold"] for x in confirmation_scores)
        correct_accepted=sum(correct and score>=best["threshold"] for correct,score
                             in zip(confirmation_correct,confirmation_scores))
        summaries[kind]={"development_best":best,
            "exposed_confirmation":{"accepted":accepted,
                                    "correct_and_accepted":correct_accepted,
                                    "total":len(EXPOSED_CONFIRMATION)}}
    return {"protocol":"development_only_ood_threshold_calibration",
            "calibration_source":"CLINC150 original oos_val only",
            "calibration_ood_count":len(ood_queries),
            "in_domain_calibration_count":len(IN_DOMAIN_CALIBRATION),
            "threshold_candidates":list(THRESHOLDS),
            "models":summaries,"prior_oos_test_used_for_selection":False,
            "independent_test_completed":False,"promotion_approved":False,
            "production_changes":False,
            "limitations":["CLINC OOS labels reflect CLINC intent ontology, not research-task-specific OOD ground truth",
                           "In-domain validation has prior research exposure",
                           "Exposed confirmation figures are not independent testing",
                           "Threshold comparison is development-only; new independent heldout required"]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--clinc-json",type=Path,required=True)
    parser.add_argument("--sha256",required=True)
    args=parser.parse_args()
    result=calibrate(read_oos_validation(args.clinc_json,args.sha256))
    result["source_sha256"]=args.sha256
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":main()
