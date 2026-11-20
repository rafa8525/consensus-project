"""AGI Milestone 9: paired replicated validation, immutable confirmation test.

The confirmation set is newly hand-authored (NOT external/independent provenance).
Fixed candidate hyperparameters derive from Milestone 8; no tuning on confirmation.
"""
import hashlib
import json
import random
import statistics
from collections import Counter
from local_inference import TRAIN, LABELS, fit, predict
from model_improvement_experiment import VALIDATION, TEST as PRIOR_TEST, train_char, predict_char

SEEDS = (7, 19, 43, 71, 101)
FOLDS = 5
N = 3
ALPHA = 0.5
# These strings are not drawn from any third-party evaluation dataset.
CONFIRMATION = [
 ("design_experiment", "devise a factorial trial for the learning mechanism"),
 ("design_experiment", "establish controls before optimizing the algorithm"),
 ("design_experiment", "specify a reproducible prototype comparison"),
 ("design_experiment", "structure an ablation of the new model components"),
 ("design_experiment", "budget trials to distinguish competing learners"),
 ("design_experiment", "construct a protocol with predefined checkpoints"),
 ("evaluate_evidence", "estimate the robustness of observed results"),
 ("evaluate_evidence", "inspect measurement uncertainty in repeated runs"),
 ("evaluate_evidence", "determine whether improvements survive replication"),
 ("evaluate_evidence", "measure error variance across test cohorts"),
 ("evaluate_evidence", "review quantitative signals collected from trials"),
 ("evaluate_evidence", "test the reliability of the experimental evidence"),
 ("review_hypothesis", "identify alternative causal explanations for a finding"),
 ("review_hypothesis", "consider whether a conjecture could be refuted"),
 ("review_hypothesis", "challenge hidden premises in the proposed explanation"),
 ("review_hypothesis", "evaluate rival theories explaining the observation"),
 ("review_hypothesis", "inspect potential confounders before drawing conclusions"),
 ("review_hypothesis", "question a research claim for unsupported assumptions"),
]

def macro_f1(actual, predicted):
    values = []
    for label in LABELS:
        tp = sum(y == label and p == label for y, p in zip(actual, predicted))
        fp = sum(y != label and p == label for y, p in zip(actual, predicted))
        fn = sum(y == label and p != label for y, p in zip(actual, predicted))
        values.append(0.0 if 2*tp+fp+fn == 0 else 2*tp/(2*tp+fp+fn))
    return sum(values)/len(values)

def predictions(training, evaluation):
    baseline=fit(training)
    candidate=train_char(training, n=N, alpha=ALPHA)
    return ([predict(baseline,text)["label"] for _,text in evaluation],
            [predict_char(candidate,text) for _,text in evaluation])

def split_indices(examples, seed):
    rng=random.Random(seed)
    buckets={label:[] for label in LABELS}
    for i,(label,_) in enumerate(examples):
        buckets[label].append(i)
    folds=[[] for _ in range(FOLDS)]
    for label in LABELS:
        ids=buckets[label][:]
        if len(ids)<FOLDS: raise ValueError("Not enough samples in each class")
        rng.shuffle(ids)
        for i,idx in enumerate(ids):
            folds[i%FOLDS].append(idx)
    return [sorted(x) for x in folds]

def paired_bootstrap_interval(a, b, seed=4242, n=1000):
    """Percentile interval of candidate-minus-baseline *paired accuracy*."""
    if len(a)!=len(b) or not a: raise ValueError("Mismatched paired outcomes")
    rng=random.Random(seed)
    differences=[]
    for _ in range(n):
        ids=[rng.randrange(len(a)) for _ in a]
        differences.append(sum(b[i]-a[i] for i in ids)/len(ids))
    differences.sort()
    return [round(differences[int(.025*n)],6),round(differences[min(n-1,int(.975*n))],6)]

def run():
    development = TRAIN + VALIDATION  # Prior TEST remains excluded: it was already examined.
    if len({x.lower() for _,x in development})!=len(development):
        raise ValueError("Duplicate development text")
    all_sets=(development,PRIOR_TEST,CONFIRMATION)
    sets=[{x.strip().lower() for _,x in xs} for xs in all_sets]
    if sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2]:
        raise ValueError("Dataset leakage")
    splits=[]
    for seed in SEEDS:
        allfolds=split_indices(development,seed)
        for index,held in enumerate(allfolds):
            held_set=set(held)
            training=[row for i,row in enumerate(development) if i not in held_set]
            evaluation=[development[i] for i in held]
            bp,cp=predictions(training,evaluation)
            actual=[label for label,_ in evaluation]
            splits.append({"seed":seed,"fold":index,"n":len(actual),
                "baseline_accuracy":sum(y==p for y,p in zip(actual,bp))/len(actual),
                "candidate_accuracy":sum(y==p for y,p in zip(actual,cp))/len(actual),
                "baseline_macro_f1":macro_f1(actual,bp),
                "candidate_macro_f1":macro_f1(actual,cp)})
    baseline_cv=statistics.mean(x["baseline_macro_f1"] for x in splits)
    candidate_cv=statistics.mean(x["candidate_macro_f1"] for x in splits)
    # One final confirmation comparison; no choice or tuning based on these labels.
    bp,cp=predictions(development,CONFIRMATION)
    gold=[y for y,_ in CONFIRMATION]
    bs=[int(p==y) for p,y in zip(bp,gold)]
    cs=[int(p==y) for p,y in zip(cp,gold)]
    interval=paired_bootstrap_interval(bs,cs)
    # These criteria must all hold before an *independent* research promotion.
    # This gate cannot establish external generalization given handcrafted data.
    stricter_gate=(candidate_cv-baseline_cv>=0.05 and
                   sum(cs)-sum(bs)>=2 and interval[0]>0)
    digest=hashlib.sha256(json.dumps({"development":development,
        "already_seen_test":PRIOR_TEST,"confirmation":CONFIRMATION},
        sort_keys=True,separators=(",",":")).encode()).hexdigest()
    def summary(values):
        return {"correct":sum(values),"total":len(values),
                "accuracy":round(sum(values)/len(values),6)}
    return {"experiment":"replicated_validation_with_confirmation_v1",
        "dataset_sha256":digest,"split_policy":"5-fold stratified x 5 fixed seeds",
        "number_of_folds":len(splits),"development_count":len(development),
        "confirmation_count":len(CONFIRMATION),"candidate_hyperparameters":{"n":N,"alpha":ALPHA},
        "cv_macro_f1":{"baseline":round(baseline_cv,6),
                       "candidate":round(candidate_cv,6),
                       "delta":round(candidate_cv-baseline_cv,6)},
        "confirmation":{"baseline":summary(bs),"candidate":summary(cs),
                         "paired_accuracy_gain_95pct_bootstrap_ci":interval},
        "promotion_approved":False,
        "replication_gate_passed":stricter_gate,
        "promotion_rule":"requires external-provenance validation beyond handcrafted confirmation",
        "production_changes":False,
        "limitations":["Small hand-authored text corpus, not independently sourced",
                       "Repeated folds are correlated; do not treat 25 folds as independent experiments",
                       "Bootstrap interval is descriptive at n=18 and not a guarantee of generalization"]}
if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
