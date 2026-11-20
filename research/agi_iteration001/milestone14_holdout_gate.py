"""Milestone 14: frozen-threshold, externally reviewed four-way holdout gate.

Intake checks are mechanical and do not establish that human attestations are true.
A single run reports observations, never approves a research or production promotion.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from local_inference import TRAIN, LABELS, fit as fit_word, predict as predict_word
from model_improvement_experiment import VALIDATION, TEST as PRIOR_TEST, train_char, predict_char
from replicated_model_evaluation import CONFIRMATION
from external_benchmark_gate import STRESS, classification_metrics
from clinc_ood_protocol import known_fraction

FROZEN = {"word": 0.15, "char": 0.50}
FROZEN_TRAIN = TRAIN
MAX_BYTES = 1024 * 1024
MAX_ROWS = 2000
MIN_PER_LABEL = 10
ALL_LABELS = frozenset(LABELS) | {"out_of_scope"}

def normalize(value):
    if not isinstance(value,str): return ""
    return " ".join(re.findall(r"[a-z]+",value.lower()))

def _known_examples():
    return {normalize(text) for _,text in
            (TRAIN + VALIDATION + PRIOR_TEST + CONFIRMATION + STRESS)}

def inspect_holdout(data, manifest):
    if not isinstance(data,bytes) or len(data)>MAX_BYTES:
        raise ValueError("Holdout missing or oversized")
    if not isinstance(manifest,dict):raise ValueError("Manifest required")
    required=("sha256","source_url","license","dataset_id","collection_method",
              "annotation_guidelines_url","reviewer_1","reviewer_2","review_utc",
              "training_data_excluded","validation_data_excluded")
    if any(k not in manifest for k in required):
        raise ValueError("Missing provenance or review fields")
    if manifest["sha256"]!=hashlib.sha256(data).hexdigest():
        raise ValueError("Holdout checksum mismatch")
    for key in ("source_url","license","dataset_id","collection_method",
                "annotation_guidelines_url","reviewer_1","reviewer_2","review_utc"):
        if not isinstance(manifest[key],str) or not manifest[key].strip():
            raise ValueError("Empty provenance detail")
    if not (manifest["source_url"].startswith("https://") and
            manifest["annotation_guidelines_url"].startswith("https://")):
        raise ValueError("HTTPS reference required")
    if manifest["reviewer_1"]==manifest["reviewer_2"]:
        raise ValueError("Distinct reviewers required")
    if manifest["training_data_excluded"] is not True or manifest["validation_data_excluded"] is not True:
        raise ValueError("Explicit exclusion attestations required")
    try: lines=data.decode("utf8").splitlines()
    except UnicodeDecodeError as exc:raise ValueError("Invalid encoding") from exc
    if not 4*MIN_PER_LABEL<=len(lines)<=MAX_ROWS:
        raise ValueError("Insufficient or excessive holdout")
    rows=[]
    known=_known_examples()
    seen=set()
    counts={y:0 for y in ALL_LABELS}
    for line in lines:
        try: item=json.loads(line)
        except json.JSONDecodeError as exc:raise ValueError("Malformed JSONL") from exc
        if not isinstance(item,dict) or set(item)!={"label","text"}:
            raise ValueError("Only label/text allowed")
        label,text=item["label"],item["text"]
        if not isinstance(label,str) or label not in ALL_LABELS:
            raise ValueError("Unsupported label")
        if not isinstance(text,str) or not 4<=len(text)<=500:
            raise ValueError("Invalid text")
        key=normalize(text)
        if len(key)<4 or key in seen or key in known:
            raise ValueError("Duplicate or earlier dataset leakage")
        seen.add(key)
        rows.append((label,text))
        counts[label]+=1
    if min(counts.values())<MIN_PER_LABEL:
        raise ValueError("Class balance minimum not met")
    return rows

def evaluate(rows):
    if not rows:raise ValueError("Empty holdout")
    baseline=fit_word(FROZEN_TRAIN)
    candidate=train_char(FROZEN_TRAIN,n=3,alpha=0.5)
    results={}
    for kind,model,predictor in (
        ("word",baseline,lambda s:predict_word(baseline,s)["label"]),
        ("char",candidate,lambda s:predict_char(candidate,s))):
        vocab=set(model["vocab"])
        records=[]
        for expected,text in rows:
            score=known_fraction(text,vocab,kind)
            accepted=score>=FROZEN[kind]
            actual=predictor(text) if accepted else "out_of_scope"
            records.append((expected,actual,accepted))
        domain=[(exp,actual) for exp,actual,_ in records if exp!="out_of_scope"]
        ood=[(exp,actual) for exp,actual,_ in records if exp=="out_of_scope"]
        correct=sum(exp==actual for exp,actual in domain)
        false_accept=sum(actual!="out_of_scope" for _,actual in ood)
        # Macro-F1 including the reject class, unlike the older 3-way classifier.
        labels=tuple(LABELS)+("out_of_scope",)
        per_label={}
        for label in labels:
            tp=sum(exp==label and actual==label for exp,actual,_ in records)
            fp=sum(exp!=label and actual==label for exp,actual,_ in records)
            fn=sum(exp==label and actual!=label for exp,actual,_ in records)
            per_label[label]=0.0 if 2*tp+fp+fn==0 else 2*tp/(2*tp+fp+fn)
        results[kind]={
          "frozen_threshold":FROZEN[kind],
          "in_domain_correct_and_accepted":correct,
          "in_domain_total":len(domain),
          "ood_false_accept_count":false_accept,
          "ood_total":len(ood),
          "ood_false_accept_rate":round(false_accept/len(ood),6) if ood else None,
          "four_way_macro_f1":round(sum(per_label.values())/len(labels),6),
        }
    return {"experiment":"milestone14_frozen_threshold_four_way_holdout",
            "results":results,"model_training_rows":len(TRAIN),
            "candidate_model":"word_plus_character_trigram_nb_alpha_0.5",
            "holdout_used_for_tuning":False,
            "human_provenance_independently_verified":False,
            "promotion_approved":False,"production_changes":False,
            "limitations":["Manifest and reviewer names are self-declarations, not verified identities",
              "Independent test may be executed once only; reuse is exploratory thereafter",
              "Earlier CLINC labels do not map directly to this four-label research ontology"]}

def run(path,manifest_path):
    p=Path(path); m=Path(manifest_path)
    if p.is_symlink() or m.is_symlink() or not p.is_file() or not m.is_file():
        raise ValueError("Untrusted input paths")
    if p.stat().st_size>MAX_BYTES or m.stat().st_size>20000:
        raise ValueError("Input size exceeded")
    manifest=json.loads(m.read_text(encoding="utf8"))
    rows=inspect_holdout(p.read_bytes(),manifest)
    result=evaluate(rows)
    result["holdout_sha256"]=manifest["sha256"]
    result["dataset_id"]=manifest["dataset_id"]
    result["holdout_row_count"]=len(rows)
    result["provenance_status"]="declarations_only_review_required"
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--holdout-jsonl",type=Path,required=True)
    parser.add_argument("--manifest",type=Path,required=True)
    a=parser.parse_args()
    print(json.dumps(run(a.holdout_jsonl,a.manifest),sort_keys=True,indent=2))
if __name__=="__main__":main()
