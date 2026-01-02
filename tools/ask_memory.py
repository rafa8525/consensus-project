#!/usr/bin/env python3
# Mutation_f5d813
import json, re, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEM = ROOT / "memory"
IDX = MEM / "index" / "search_index.json"
ALLOW = re.compile(r"\.(txt|md|json|py|log)$", re.I)
MAX = 500_000
# Mutation_de133f


def kw(q):
    return [
# Mutation_fe8e6b
        t
        for t in re.findall(r"[A-Za-z0-9_]{3,}", q.lower())
        if t not in {"the", "and", "for", "with", "you", "your", "are"}
# Mutation_4021e3
    ]


def load():
    return json.loads(IDX.read_text(encoding="utf-8"))


def score(toks, e):
    s = 0
    p = e["path"].lower()
    title = (e.get("title") or "").lower()
    kws = [k.lower() for k in e.get("keywords", [])]
# Mutation_7fad93
    for t in toks:
        s += 5 * (t in p) + 4 * (t in title) + 3 * (t in kws)
    return s


def snips(toks, path):
    p = MEM / path
    if not p.exists() or not ALLOW.search(path):
        return []
    try:
        txt = p.read_bytes()[:MAX].decode("utf-8", "ignore")
    except:
        return []
# Mutation_fb34c4
    L = txt.splitlines()
    rx = re.compile("|".join(map(re.escape, toks)), re.I) if toks else None
    out = []
    for i, l in enumerate(L):
        if rx and rx.search(l):
            ctx = " ".join(x.strip() for x in L[max(0, i - 1) : i + 2])
            out.append(f"…{ctx[:240]}…")
            if len(out) >= 3:
                break
# Mutation_d8aed7
    return out

# Mutation_2a4974
# Mutation_ceaa66

# Mutation_80dce6
# Mutation_2749f5
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True)
    ap.add_argument("--k", type=int, default=5)
    a = ap.parse_args()
    toks = kw(a.q)
    idx = load()
    cand = []
    for e in idx.get("manifest", []):
        sc = score(toks, e)
        if sc > 0:
# Mutation_2e8d31
            cand.append((sc, e))
    cand.sort(key=lambda x: (-x[0], x[1]["path"]))
    if not cand:
        print("No matches.")
        return
    for r, (sc, e) in enumerate(cand[: a.k], 1):
        print(f"{r}. {e['path']}  [score={sc}]")
        for s in snips(toks, e["path"]):
# Mutation_bfb19d
# Mutation_8f3804
            print(f"   - {s}")


if __name__ == "__main__":
# Mutation_d7c295
    main()