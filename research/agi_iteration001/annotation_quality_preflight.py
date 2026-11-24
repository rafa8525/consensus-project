"""Research-only annotation quality preflight. No texts, keys, I/O, or external calls.

Input is a caller-supplied in-memory sequence of anonymous labeling *metadata*.
This function does not establish provenance, real human independence or consent.
Do not run on live data without separate authorization and secure local handling.
"""
from collections import Counter
from local_inference import LABELS

MIN_TOTAL=60
MIN_PER_CLASS=20
MIN_AGREEMENT=0.80
MIN_KAPPA=0.70

def annotation_quality(records):
    if not isinstance(records,(tuple,list)) or len(records)>5000:
        raise ValueError("Invalid annotation metadata collection")
    seen=set()
    two_by_two=Counter()
    first=Counter()
    second=Counter()
    final=Counter()
    problems=Counter()
    for row in records:
        if not isinstance(row,dict) or set(row)!={"item_id","annotator_a","annotator_b",
                "vote_a","vote_b","adjudicator","adjudicated_label"}:
            raise ValueError("Unexpected annotation metadata fields")
        item=row["item_id"]
        ids=[row[x] for x in ("annotator_a","annotator_b","adjudicator")]
        if not isinstance(item,str) or not (1<=len(item)<=64) or not item.isascii() or not all(
                x.isalnum() or x in "-_" for x in item):
            raise ValueError("Invalid pseudonymous record ID")
        if item in seen:
            raise ValueError("Duplicate record ID")
        seen.add(item)
        if any(not isinstance(x,str) or not (1<=len(x)<=64) or not x.isascii() or not all(
                c.isalnum() or c in "-_" for c in x) for x in ids):
            raise ValueError("Invalid pseudonymous annotator ID")
        if len(set(ids))!=3:
            raise ValueError("Annotator and adjudicator must have distinct IDs")
        a,b,out=row["vote_a"],row["vote_b"],row["adjudicated_label"]
        if a not in LABELS or b not in LABELS or out not in LABELS:
            raise ValueError("Unknown task-intent label")
        if a==b and out!=a:
            raise ValueError("Unexplained override of matching votes")
        if a!=b and not row["adjudicator"]:
            raise ValueError("Disagreement lacks adjudicator")
        two_by_two[(a,b)]+=1
        first[a]+=1
        second[b]+=1
        final[out]+=1
        if a!=b:problems["disagreements"]+=1
    n=len(records)
    if n:
        observed=sum(two_by_two[(x,x)] for x in LABELS)/n
        expected=sum(first[x]*second[x] for x in LABELS)/(n*n)
        # Degenerate marginals have no chance-corrected reliability estimate.
        kappa=None if expected>=1.0 else (observed-expected)/(1.0-expected)
    else:
        observed=0.0
        kappa=None
    counts={label:final[label] for label in LABELS}
    quantity_pass=n>=MIN_TOTAL and all(counts[x]>=MIN_PER_CLASS for x in LABELS)
    reliability_pass=observed>=MIN_AGREEMENT and kappa is not None and kappa>=MIN_KAPPA
    return {
        "evaluation":"annotation_metadata_preflight_v1",
        "record_count":n,
        "adjudicated_class_counts":counts,
        "disagreement_count":problems["disagreements"],
        "raw_agreement":round(observed,6),
        "cohens_kappa":None if kappa is None else round(kappa,6),
        "count_gate_passed":quantity_pass,
        "reliability_gate_passed":reliability_pass,
        "annotation_metadata_quality_passed":quantity_pass and reliability_pass,
        "data_imported":False,
        "actual_human_independence_verified":False,
        "consent_or_rights_verified":False,
        "near_duplicate_review_verified":False,
        "independent_provenance_verified":False,
        "external_validation_authorized":False,
        "promotion_approved":False,
        "limitations":[
            "In-memory metadata only; never validates real annotation provenance",
            "Agreement is not equivalent to correctness or label independence",
            "Source, rights, near duplicates and consent require independent human review",
        ],
    }

if __name__=="__main__":
    # Intentionally no synthetic output resembling a real reviewed corpus.
    print("Annotation quality preflight is available; no dataset supplied or evaluated.")
