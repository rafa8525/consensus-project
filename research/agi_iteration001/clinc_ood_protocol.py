"""Milestone 11: independently sourced CLINC150-compatible OOD protocol.

It NEVER re-labels CLINC150 intents as the 3 research-task classes.
No network fetch, runtime writes, automatic promotion, or credential use.
"""
import argparse
import hashlib
import json
from pathlib import Path
from local_inference import LABELS, fit as train_word, predict as predict_word, tokens
from model_improvement_experiment import _features, train_char, predict_char
from replicated_model_evaluation import DEVELOPMENT, CONFIRMATION

MAX_FILE_BYTES = 5_000_000
DEFAULT_SAMPLE_LIMIT = 200
MIN_OOD = 30
# Fixed threshold; not tuned on the CLINC150 evaluation set.
MIN_KNOWN_FRACTION = 0.25

def read_original(path, expected_sha256, limit=DEFAULT_SAMPLE_LIMIT):
    """Read CLINC150 data_small/data_full JSON, out-of-scope test subset only."""
    path=Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Dataset is missing or symlinked")
    if path.stat().st_size>MAX_FILE_BYTES:
        raise ValueError("Dataset exceeds byte cap")
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError("Source SHA256 mismatch")
    if not 30<=limit<=1000:
        raise ValueError("Sample cap out of range")
    try:
        payload=json.loads(raw)
    except (ValueError,UnicodeDecodeError) as exc:
        raise ValueError("Dataset is not valid UTF8 JSON") from exc
    if not isinstance(payload,dict):
        raise ValueError("Expected CLINC150 split object")
    rows=payload.get("oos_test")
    if not isinstance(rows,list) or len(rows)<MIN_OOD:
        raise ValueError("Out-of-scope test split missing or insufficient")
    texts=[]
    seen=set()
    for row in rows:
        if not isinstance(row,list) or len(row)!=2 or not isinstance(row[0],str) or row[1]!="oos":
            raise ValueError("Malformed oos_test row")
        txt=row[0].strip()
        if not 4<=len(txt)<=500:raise ValueError("Out-of-scope text length invalid")
        key=" ".join(tokens(txt))
        if not key or key in seen:continue
        seen.add(key)
        texts.append(txt)
    if len(texts)<MIN_OOD:raise ValueError("Too few distinct out-of-scope examples")
    # Stable hash-ranked selection (not tuned on model predictions).
    return sorted(texts,key=lambda t:(hashlib.sha256(t.encode()).hexdigest(),t))[:limit]

def known_fraction(text,vocab,mode):
    if mode=="word":
        feats=tokens(text)
    elif mode=="char":
        feats=list(_features(text,3).elements())
    else:
        raise ValueError("Unknown feature mode")
    return sum(x in vocab for x in feats)/len(feats) if feats else 0.0

def evaluate_ood(oos):
    word=train_word(DEVELOPMENT)
    char=train_char(DEVELOPMENT,n=3,alpha=0.5)
    wb_vocab=set(word["vocab"])
    ch_vocab=char["vocab"]
    def probe(mode,vocab,predictor):
        in_rows=[]
        for truth,text in CONFIRMATION:
            predicted=predictor(text)
            fraction=known_fraction(text,vocab,mode)
            in_rows.append((predicted==truth,fraction>=MIN_KNOWN_FRACTION))
        out_accept=sum(known_fraction(text,vocab,mode)>=MIN_KNOWN_FRACTION for text in oos)
        good=sum(correct and accepted for correct,accepted in in_rows)
        return {"confirmation_correct_and_accepted":good,
                "confirmation_total":len(in_rows),
                "confirmation_coverage":round(sum(a for _,a in in_rows)/len(in_rows),6),
                "out_of_scope_accepted":out_accept,
                "out_of_scope_total":len(oos),
                "out_of_scope_false_accept_rate":round(out_accept/len(oos),6)}
    baseline=probe("word",wb_vocab,lambda text:predict_word(word,text)["label"])
    candidate=probe("char",ch_vocab,lambda text:predict_char(char,text))
    return {"protocol":"clinc150_out_of_scope_exploratory_v1",
        "scope":"cross_domain_rejection_only",
        "threshold":MIN_KNOWN_FRACTION,
        "baseline":baseline,"candidate":candidate,
        "production_changes":False,"promotion_approved":False,
        "limitations":["CLINC150 out-of-scope intents are relative to CLINC150, not validated labels for our research-task classifier",
                       "Vocabulary-coverage heuristic is not calibrated model confidence",
                       "The in-scope comparison uses a small hand-authored confirmation set",
                       "No automatic choice of threshold, model, or promotion from test scores"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--clinc-json",type=Path,required=True)
    p.add_argument("--sha256",required=True)
    p.add_argument("--sample",type=int,default=DEFAULT_SAMPLE_LIMIT)
    a=p.parse_args()
    if len(a.sha256)!=64 or any(ch not in "0123456789abcdef" for ch in a.sha256):
        p.error("sha256 must be lowercase 64 hexadecimal characters")
    texts=read_original(a.clinc_json,a.sha256,a.sample)
    outcome=evaluate_ood(texts)
    outcome["dataset_sha256"]=a.sha256
    outcome["source"]="CLINC150 original oos_test; validate license and exact source independently"
    print(json.dumps(outcome,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
