"""Milestone 10: resource-metered robustness and external-dataset intake gate.

Research-only. No web requests, credential access, automatic promotion or deployment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import time
import tracemalloc
from pathlib import Path
from local_inference import LABELS, TRAIN, fit as fit_word, predict as predict_word
from model_improvement_experiment import VALIDATION, train_char, predict_char
from replicated_model_evaluation import CONFIRMATION, macro_f1

# New fixed probe set: these are INTERNAL hand-authored stress probes, NOT independent data.
STRESS = [
 ("design_experiment", "devise controlled trials with resource limits"),
 ("design_experiment", "set up ablations and comparison groups"),
 ("design_experiment", "specify how we would test a different learner"),
 ("design_experiment", "establish an experimental treatment and control"),
 ("evaluate_evidence", "calculate confidence bounds for measured gains"),
 ("evaluate_evidence", "audit performance figures for numerical errors"),
 ("evaluate_evidence", "assess reproducibility of reported outcomes"),
 ("evaluate_evidence", "compare test evidence from repeated measurements"),
 ("review_hypothesis", "criticize the premise behind the prediction"),
 ("review_hypothesis", "identify competing explanations and confounding causes"),
 ("review_hypothesis", "challenge the research conjecture's assumptions"),
 ("review_hypothesis", "ask what would falsify the proposed mechanism"),
]
DEVELOPMENT=TRAIN+VALIDATION
MAX_ITEMS=5000
MAX_BYTES=1024*1024
MIN_ITEMS=30

def _normalize(s):
    return " ".join(re.findall(r"[a-z]+",s.lower()))

def validate_external(data_bytes, manifest, development=DEVELOPMENT,
                      prior_tests=CONFIRMATION):
    """Fail closed for missing or implausible provenance and leakage.

    An operator must independently verify the provenance declaration; this
    function is not an external-source verifier.
    """
    if len(data_bytes)>MAX_BYTES: raise ValueError("Dataset exceeds size limit")
    if not isinstance(manifest,dict): raise ValueError("Invalid manifest")
    required=("sha256","source_url","license","dataset_id","annotator_id",
              "collection_method","heldout_for")
    if any(not isinstance(manifest.get(k),str) or not manifest[k].strip()
           for k in required): raise ValueError("Missing provenance fields")
    if manifest["sha256"]!=hashlib.sha256(data_bytes).hexdigest():
        raise ValueError("Dataset checksum mismatch")
    if not manifest["source_url"].startswith("https://"):
        raise ValueError("HTTPS source reference required")
    if manifest["heldout_for"]!="research-task-classification-v1":
        raise ValueError("Dataset purpose mismatch")
    try:
        lines=data_bytes.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError("Non UTF-8 dataset") from exc
    if not MIN_ITEMS<=len(lines)<=MAX_ITEMS: raise ValueError("Insufficient or excessive examples")
    expected={_normalize(text) for _,text in development+prior_tests+STRESS}
    records=[]
    observed=set()
    counts={label:0 for label in LABELS}
    for line in lines:
        try: row=json.loads(line)
        except json.JSONDecodeError as exc: raise ValueError("Invalid JSONL") from exc
        if not isinstance(row,dict) or set(row)!={"label","text"}:
            raise ValueError("Only label and text allowed")
        label,text=row["label"],row["text"]
        if label not in counts or not isinstance(text,str) or not 4<=len(text)<=500:
            raise ValueError("Bad label/text")
        norm=_normalize(text)
        if len(norm)<4 or norm in observed or norm in expected:
            raise ValueError("Duplicate or development/test leakage")
        observed.add(norm)
        counts[label]+=1
        records.append((label,text))
    if min(counts.values())<8: raise ValueError("Class imbalance or insufficient per-class examples")
    return records

def classification_metrics(rows, predictions):
    actual=[label for label,_ in rows]
    if len(actual)!=len(predictions): raise ValueError("Bad prediction count")
    return {"accuracy":round(sum(a==b for a,b in zip(actual,predictions))/len(actual),6),
            "macro_f1":round(macro_f1(actual,predictions),6),
            "correct":sum(a==b for a,b in zip(actual,predictions)),
            "total":len(actual)}

def _measure(fn):
    tracemalloc.start()
    try:
        start=time.perf_counter()
        result=fn()
        elapsed=time.perf_counter()-start
        _current,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result,{"elapsed_ms":round(elapsed*1000,3),"peak_traced_kib":round(peak/1024,2)}

def benchmark(rows=STRESS):
    # Fixed selected Milestone-8 model; never fit to the evaluation set.
    baseline,baseline_train=_measure(lambda: fit_word(DEVELOPMENT))
    candidate,candidate_train=_measure(lambda: train_char(DEVELOPMENT,n=3,alpha=0.5))
    old,old_inference=_measure(lambda:[predict_word(baseline,text)["label"] for _,text in rows])
    new,new_inference=_measure(lambda:[predict_char(candidate,text) for _,text in rows])
    return {"evaluation_kind":"internal_hand_authored_stress" if rows is STRESS else "manifest_supplied",
            "sample_count":len(rows),"baseline":{"metrics":classification_metrics(rows,old),
              "training":baseline_train,"inference":old_inference},
            "candidate":{"metrics":classification_metrics(rows,new),
              "training":candidate_train,"inference":new_inference},
            "production_changes":False,"promotion_approved":False,
            "resource_measurement":"Python tracemalloc allocations, not process RSS or CPU budget",
            "limitations":["Stress probes are not independently sourced",
                           "Runtime and allocation timings fluctuate by host and run",
                           "External manifests are declarations; human provenance review required"]}

def run_external(path,manifest_path):
    path=Path(path); manifest_path=Path(manifest_path)
    if path.is_symlink() or manifest_path.is_symlink():
        raise ValueError("Symlinks forbidden")
    if not path.is_file() or not manifest_path.is_file() or manifest_path.stat().st_size>20000:
        raise ValueError("Missing or oversized file")
    raw=path.read_bytes()
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    rows=validate_external(raw,manifest)
    result=benchmark(rows)
    result["evaluation_kind"]="externally_declared_unverified"
    result["dataset_sha256"]=manifest["sha256"]
    result["dataset_id"]=manifest["dataset_id"]
    result["independent_provenance_verified"]=False
    result["promotion_approved"]=False
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--external-jsonl",type=Path)
    p.add_argument("--manifest",type=Path)
    a=p.parse_args()
    if bool(a.external_jsonl)!=bool(a.manifest):
        p.error("external-jsonl and manifest must be supplied together")
    result=run_external(a.external_jsonl,a.manifest) if a.external_jsonl else benchmark()
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__": main()
