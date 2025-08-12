#!/usr/bin/env python3
import json, re, argparse, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEM  = ROOT / "memory"
IDX  = MEM / "index" / "search_index.json"
LOG  = MEM / "logs" / "voice"
LOG.mkdir(parents=True, exist_ok=True)

ALLOW_EXT = re.compile(r"\.(txt|md|json|py|log)$", re.I)
MAX_BYTES = 500_000

def load_index():
    if not IDX.exists():
        print("Index missing; run tools/absorb_memory.py first.")
        return None
    return json.loads(IDX.read_text(encoding="utf-8"))

def score_entry(qtoks, e):
    s = 0
    p = e["path"].lower()
    title = (e.get("title") or "").lower()
    kw = [k.lower() for k in e.get("keywords", [])]
    for t in qtoks:
        if t in p: s += 5
        if t in title: s += 4
        if t in kw: s += 3
    return s

def snippets(qtoks, path):
    p = MEM / path
    if not p.exists() or not ALLOW_EXT.search(path): return []
    try:
        b = p.read_bytes()[:MAX_BYTES]
        text = b.decode("utf-8", errors="ignore")
    except Exception:
        return []
    lines = text.splitlines()
    hits=[]
    rx = re.compile("|".join(re.escape(t) for t in qtoks), re.I) if qtoks else None
    for i, line in enumerate(lines):
        if rx and rx.search(line):
            ctx = " ".join(l.strip() for l in lines[max(0,i-1): i+2])
            hits.append(f"…{ctx[:240]}…")
        if len(hits)>=3: break
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True, help="query")
    ap.add_argument("--k", type=int, default=5, help="results")
    ap.add_argument("--snippets", type=int, default=3, help="snippets per top file")
    args = ap.parse_args()

    idx = load_index()
    if not idx:
        return
    qtoks = [t for t in re.findall(r"[A-Za-z0-9_]{2,}", args.q.lower()) if t not in {"the","and","for","with","you","your","are"}]
    scored = []
    for e in idx.get("manifest", []):
        sc = score_entry(qtoks, e)
        if sc>0: scored.append((sc, e))
    scored.sort(key=lambda x: (-x[0], x[1]["path"]))

    out_lines=[]
    out_lines.append(f"# Q: {args.q}")
    if not scored:
        out_lines.append("No matches found.")
    else:
        for rank,(sc,e) in enumerate(scored[:args.k], start=1):
            path=e["path"]; sz=e["size"]; mtime=e["mtime"]
            out_lines.append(f"{rank}. {path}  [score={sc} size={sz} mtime={mtime}]")
            for snip in snippets(qtoks, path)[:args.snippets]:
                out_lines.append(f"   - {snip}")

    # write voice log and print
    LOG.joinpath("ask_log.txt").parent.mkdir(parents=True, exist_ok=True)
    with open(LOG/"ask_log.txt","a",encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] Q={args.q}\n")
    print("\n".join(out_lines))

if __name__ == "__main__":
    main()
