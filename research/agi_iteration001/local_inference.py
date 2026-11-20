"""Offline trained multinomial Naive Bayes classifier; not an LLM or general reasoning agent."""
import hashlib,json,math,re
from collections import Counter
from pathlib import Path

LABELS=('design_experiment','evaluate_evidence','review_hypothesis')
TRAIN=[
('design_experiment','define baseline dataset split and experiment budget'),
('design_experiment','plan model architecture and training procedure'),
('design_experiment','design controlled trial with success criteria'),
('design_experiment','construct new learning experiment and test plan'),
('design_experiment','choose benchmark samples and allocate compute'),
('design_experiment','specify training schedule optimizer and parameters'),
('evaluate_evidence','evaluate results against baseline metrics'),
('evaluate_evidence','measure accuracy and examine regression metrics'),
('evaluate_evidence','verify reproducibility and compare benchmark outcomes'),
('evaluate_evidence','audit training logs and assessment artifacts'),
('evaluate_evidence','analyze test scores and confidence intervals'),
('evaluate_evidence','inspect held out evaluation statistics and errors'),
('review_hypothesis','review scientific hypothesis for falsifiability'),
('review_hypothesis','critique assumptions and identify confounding variables'),
('review_hypothesis','check claim for alternative explanations'),
('review_hypothesis','question research theory and possible bias'),
('review_hypothesis','consider causal prediction and competing hypotheses'),
('review_hypothesis','assess plausible mechanisms and counterarguments')]
TEST=[
('design_experiment','design benchmark for a new training approach'),
('design_experiment','plan controlled model experiment'),
('evaluate_evidence','compare validation accuracy with previous results'),
('evaluate_evidence','inspect independent evaluation metrics'),
('review_hypothesis','critique a scientific claim and its assumptions'),
('review_hypothesis','identify hidden confounders in the hypothesis')]

def tokens(text): return re.findall(r'[a-z]+',text.lower())[:128]

def fit(examples=TRAIN):
    counts={k:Counter() for k in LABELS}
    docs=Counter()
    for label,s in examples:
        if label not in counts: raise ValueError('Unsupported label')
        docs[label]+=1
        counts[label].update(tokens(s))
    vocab=sorted(set().union(*(set(v) for v in counts.values())))
    return {'schema':1,'labels':list(LABELS),'docs':dict(docs),
            'counts':{k:dict(counts[k]) for k in LABELS},'vocab':vocab,
            'training_count':len(examples),'model_type':'multinomial_naive_bayes'}

def predict(model,text):
    if not isinstance(text,str) or not 0<len(text)<=500: raise ValueError('Invalid objective')
    vocab=set(model['vocab'])
    total=sum(model['docs'].values())
    scores={}
    for label in LABELS:
        count=model['counts'][label]
        denom=sum(count.values())+len(vocab)
        s=math.log((model['docs'][label]+1)/(total+len(LABELS)))
        s+=sum(math.log((count.get(t,0)+1)/denom) for t in tokens(text) if t in vocab)
        scores[label]=s
    label=max(LABELS,key=lambda k:(scores[k],k))
    offset=max(scores.values())
    probs={k:math.exp(v-offset) for k,v in scores.items()}
    norm=sum(probs.values())
    return {'label':label,'probabilities':{k:round(probs[k]/norm,6) for k in LABELS}}

def evaluate(model,examples=TEST):
    rows=[{'expected':y,'predicted':predict(model,t)['label'],'input':t} for y,t in examples]
    n=sum(r['expected']==r['predicted'] for r in rows)
    return {'correct':n,'total':len(rows),'accuracy':n/len(rows),'predictions':rows}

def save_checkpoint(path,model):
    obj={'model':model,'evaluation':evaluate(model),
         'limitations':['Tiny hand-authored corpus','No evidence of general intelligence',
                        'Classifier is not a language model or autonomous reasoning agent']}
    canonical=json.dumps(obj,sort_keys=True,separators=(',',':'))
    obj['sha256']=hashlib.sha256(canonical.encode()).hexdigest()
    Path(path).write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return obj

def load_checkpoint(path):
    obj=json.loads(Path(path).read_text(encoding='utf-8'))
    digest=obj.pop('sha256')
    actual=hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if digest!=actual or obj['model']['schema']!=1 or obj['model']['labels']!=list(LABELS):
        raise ValueError('Model checksum/schema mismatch')
    obj['sha256']=digest
    return obj

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--checkpoint',required=True)
    args=p.parse_args()
    result=save_checkpoint(args.checkpoint,fit())
    print(json.dumps({'heldout':result['evaluation'],'sha256':result['sha256']}))
