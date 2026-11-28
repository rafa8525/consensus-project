"""AGI research experiment: compare word NB against a new character-ngrams NB.

All text and labels are original hand-authored research tasks.
Validation selects candidate hyperparameters. Test is assessed once after selection.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
from collections import Counter
from local_inference import TRAIN, LABELS, fit as fit_word, predict as predict_word

# Disjoint task texts; train rows remain local_inference.TRAIN. No use of TEST during tuning.
VALIDATION = [
 ("design_experiment","architect a repeatable trial for a novel learner"),
 ("design_experiment","schedule an ablation study with limited resources"),
 ("design_experiment","create an experimental protocol for neural adaptation"),
 ("design_experiment","outline a fair benchmark comparing two algorithms"),
 ("evaluate_evidence","quantify reliability of benchmark measurements"),
 ("evaluate_evidence","calculate error rates for multiple systems"),
 ("evaluate_evidence","check significance of validation improvements"),
 ("evaluate_evidence","audit measured outcomes using reproducible statistics"),
 ("review_hypothesis","challenge the underlying causal assumption"),
 ("review_hypothesis","find plausible rival explanations for the observation"),
 ("review_hypothesis","examine whether the thesis is falsifiable"),
 ("review_hypothesis","criticize bias within the proposed reasoning"),
]
TEST = [
 ("design_experiment","prototype an alternative optimization experiment"),
 ("design_experiment","design an unbiased evaluation protocol"),
 ("design_experiment","plan a constrained training ablation"),
 ("design_experiment","propose a comparison experiment on tiny hardware"),
 ("evaluate_evidence","compute performance uncertainty across trials"),
 ("evaluate_evidence","inspect independent measurement quality"),
 ("evaluate_evidence","compare observed error distributions"),
 ("evaluate_evidence","validate whether the reported score is repeatable"),
 ("review_hypothesis","scrutinize a conjecture for hidden assumptions"),
 ("review_hypothesis","question the mechanism behind the suggested effect"),
 ("review_hypothesis","search for confounders in a causal argument"),
 ("review_hypothesis","assess alternative theories before accepting the claim"),
]
def _features(text, n=3):
    text = re.sub(r"[^a-z]+", " ", text.lower()).strip()
    items = [f"w:{w}" for w in text.split()]
    for w in text.split():
        wrapped = "^" + w + "$"
        items.extend("c:"+wrapped[i:i+n] for i in range(max(0,len(wrapped)-n+1)))
    return Counter(items)

def train_char(examples=TRAIN,n=3,alpha=1.0):
    if n not in (3,4,5) or not 0<alpha<=10: raise ValueError("Unsupported candidate settings")
    counts={label:Counter() for label in LABELS}
    docs=Counter()
    for label,text in examples:
        if label not in counts: raise ValueError("Bad label")
        docs[label]+=1
        counts[label].update(_features(text,n))
    vocab=sorted(set().union(*(v.keys() for v in counts.values())))
    return {"n":n,"alpha":alpha,"counts":counts,"docs":docs,"vocab":set(vocab)}

def predict_char(model,text):
    features=_features(text,model["n"])
    vocab=model["vocab"]
    scores={}
    total=sum(model["docs"].values())
    for label in LABELS:
        counts=model["counts"][label]
        denom=sum(counts.values()) + model["alpha"]*len(vocab)
        score=math.log((model["docs"][label]+1)/(total+len(LABELS)))
        score+=sum(freq*math.log((counts.get(feature,0)+model["alpha"])/denom)
                   for feature,freq in features.items() if feature in vocab)
        scores[label]=score
    return max(LABELS,key=lambda label:(scores[label],label))

def score(predictor,examples):
    conf={label:{pred:0 for pred in LABELS} for label in LABELS}
    for label,text in examples:
        result=predictor(text)
        conf[label][result]+=1
    correct=sum(conf[y][y] for y in LABELS)
    total=len(examples)
    return {"correct":correct,"total":total,"accuracy":round(correct/total,6),"confusion":conf}

def run():
    baseline=fit_word()
    bp=lambda text:predict_word(baseline,text)["label"]
    base_valid=score(bp,VALIDATION)
    # Candidate settings chosen exclusively by validation; immutable test withheld.
    settings=[(n,alpha) for n in (3,4,5) for alpha in (0.5,1.0,2.0)]
    candidates=[]
    for n,alpha in settings:
        model=train_char(n=n,alpha=alpha)
        validation=score(lambda text:predict_char(model,text),VALIDATION)
        candidates.append((validation["correct"],n,alpha))
    # Deterministic tie-break to smaller n and smaller smoothing.
    best=max(candidates,key=lambda x:(x[0],-x[1],-x[2]))
    selected=train_char(n=best[1],alpha=best[2])
    candidate_valid=score(lambda text:predict_char(selected,text),VALIDATION)
    base_test=score(bp,TEST)
    candidate_test=score(lambda text:predict_char(selected,text),TEST)
    # A validation gain and internal test non-regression establish only preliminary
    # research eligibility. They NEVER authorize promotion or deployment.
    research_candidate_eligible=(candidate_valid["correct"]>base_valid["correct"] and
             candidate_test["correct"]>=base_test["correct"])
    corpus={"train":TRAIN,"validation":VALIDATION,"test":TEST}
    digest=hashlib.sha256(json.dumps(corpus,sort_keys=True).encode()).hexdigest()
    return {"experiment":"char_ngram_nb_vs_word_nb_v1",
            "split_sizes":{"train":len(TRAIN),"validation":len(VALIDATION),"test":len(TEST)},
            "dataset_sha256":digest,
            "baseline":{"validation":base_valid,"test":base_test},
            "candidate":{"n":best[1],"alpha":best[2],"validation":candidate_valid,"test":candidate_test},
            "research_candidate_eligible":research_candidate_eligible,
            "promotion_approved":False,
            "promotion_scope":"not_approved_internal_hand_authored_data",
            "production_changes":False,
            "warnings":["Hand-authored small corpus; lexical overlap may bias metrics",
                        "Validation-based hyperparameter selection; test inspected once",
                        "Promoted research candidate would require external dataset replication"]}

if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
