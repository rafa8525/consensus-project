"""Iteration 001: deterministic XOR neural-network training smoke test.
Standard-library-only; no network, external datasets, or production dependencies.
"""
import argparse
import json
import math
import random
from pathlib import Path

DATA = [(0., 0., 0.), (0., 1., 1.), (1., 0., 1.), (1., 1., 0.)]

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, x))))

def train(seed=7, epochs=12000, lr=0.7):
    rng = random.Random(seed)
    w = [[rng.uniform(-1, 1) for _ in range(3)] for _ in range(4)]
    v = [rng.uniform(-1, 1) for _ in range(5)]
    linear = [rng.uniform(-1, 1) for _ in range(3)]
    for epoch in range(epochs):
        for x, y, target in DATA:
            a = [math.tanh(row[0]*x + row[1]*y + row[2]) for row in w]
            p = sigmoid(sum(v[j]*a[j] for j in range(4)) + v[4])
            delta = p - target
            old_v = v[:]
            for j in range(4):
                v[j] -= lr * delta * a[j]
            v[4] -= lr * delta
            for j in range(4):
                dh = delta * old_v[j] * (1-a[j]*a[j])
                w[j][0] -= lr * dh * x
                w[j][1] -= lr * dh * y
                w[j][2] -= lr * dh
            q = sigmoid(linear[0]*x + linear[1]*y + linear[2])
            d = q - target
            linear[0] -= lr*d*x
            linear[1] -= lr*d*y
            linear[2] -= lr*d
    def results(kind):
        out = []
        for x, y, target in DATA:
            if kind == "modular":
                a = [math.tanh(row[0]*x + row[1]*y + row[2]) for row in w]
                p = sigmoid(sum(v[j]*a[j] for j in range(4)) + v[4])
            else:
                p = sigmoid(linear[0]*x + linear[1]*y + linear[2])
            out.append({"inputs":[int(x),int(y)],"target":int(target),
                        "probability":round(p,6),"prediction":int(p>=0.5)})
        return out
    def metrics(rows):
        correct = sum(r["prediction"] == r["target"] for r in rows)
        return {"correct":correct,"total":len(rows),"accuracy":correct/len(rows)}
    mod, base = results("modular"), results("linear")
    return {"experiment":"iteration001_xor_training_smoke_test",
            "seed":seed,"epochs":epochs,"learning_rate":lr,
            "model":"2-4-1 tanh/sigmoid MLP","parameters":17,
            "dataset":"all four XOR truth-table examples (training-set evaluation only)",
            "model_predictions":mod,"model_metrics":metrics(mod),
            "baseline":"2-input logistic regression","baseline_parameters":3,
            "baseline_predictions":base,"baseline_metrics":metrics(base),
            "limitations":["Training-set evaluation only; no held-out generalization evidence",
                           "Toy benchmark, not AGI progress",
                           "No evidence of 55-agent execution"]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="iteration001_results.json")
    args = parser.parse_args()
    result = train()
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"model_metrics":result["model_metrics"],
                      "baseline_metrics":result["baseline_metrics"]}))

if __name__ == "__main__":
    main()
