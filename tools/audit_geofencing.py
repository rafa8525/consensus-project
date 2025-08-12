#!/usr/bin/env python3
import re, json, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
MEM  = ROOT/"memory"
OUTD = MEM/"logs"/"geofencing"; OUTD.mkdir(parents=True, exist_ok=True)

TEXT_EXT = re.compile(r"\.(md|txt|log|json|yaml|yml|py)$", re.I)
MAX_BYTES = 2_000_000
KEY = re.compile(r"geofenc", re.I)

def load_text(p: Path):
    try:
        b = p.read_bytes()[:MAX_BYTES]
        return b.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def classify(line: str):
    l = line.lower()
    if any(w in l for w in ["fail", "error", "miss", "not work", "didn't", "timeout", "killed", "denied"]):
        return "failure"
    if any(w in l for w in ["feature", "should", "need to", "please add", "want", "request"]):
        return "feature"
    if any(w in l for w in ["test", "tried", "implemented", "enabled", "wired", "deployed"]):
        return "attempt"
    return "other"

def reason_extractor(line: str):
    l = line.strip()
    m = re.search(r"(because|due to|error[: ]|reason[: ])(.+)", l, re.I)
    return m.group(2).strip() if m else ""

def main():
    hits = []
    for p in MEM.rglob("*"):
        if not p.is_file(): continue
        if not TEXT_EXT.search(p.name): continue
        # skip huge binaries or archives even if *.json
        if p.stat().st_size > MAX_BYTES: continue
        txt = load_text(p)
        if not KEY.search(txt): continue
        for i, line in enumerate(txt.splitlines()):
            if KEY.search(line):
                cat = classify(line)
                reason = reason_extractor(line)
                # tiny context
                ctx_lines = txt.splitlines()[max(0,i-1): i+2]
                hits.append({
                    "path": str(p.relative_to(MEM)),
                    "line_no": i+1,
                    "category": cat,
                    "reason": reason,
                    "line": line.strip(),
                    "context": " ".join(x.strip() for x in ctx_lines)[:300]
                })

    # aggregate
    attempts  = [h for h in hits if h["category"]=="attempt"]
    failures  = [h for h in hits if h["category"]=="failure"]
    features  = [h for h in hits if h["category"]=="feature"]

    # top failure reasons (rough)
    freq = {}
    for f in failures:
        key = (f["reason"] or f["line"]).lower()
        key = re.sub(r"[^a-z0-9 ]+"," ", key)[:120].strip()
        if not key: continue
        freq[key] = freq.get(key,0)+1
    top_fail = sorted(freq.items(), key=lambda x: -x[1])[:10]

    # build markdown
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out = []
    out.append(f"# Geofencing Audit — {ts}")
    out.append(f"- Total mentions: {len(hits)}  (attempts={len(attempts)}, failures={len(failures)}, features={len(features)})")
    out.append("")
    out.append("## What we tried")
    for h in attempts[:20]:
        out.append(f"- {h['path']}:{h['line_no']} — {h['line']}")
    if len(attempts)>20: out.append(f"- … {len(attempts)-20} more")

    out.append("\n## What failed (and why)")
    for h in failures[:20]:
        why = h["reason"] or "(reason not extracted)"
        out.append(f"- {h['path']}:{h['line_no']} — {why}  \n  ↳ {h['context']}")
    if len(failures)>20: out.append(f"- … {len(failures)-20} more")

    out.append("\n### Top failure patterns (rough)")
    for k,c in top_fail:
        out.append(f"- ({c}×) {k}")

    out.append("\n## Features you asked for (from notes/logs)")
    feat_dedup = []
    for h in features[:50]:
        s = h["line"]
        if s not in feat_dedup:
            feat_dedup.append(s)
            out.append(f"- {h['path']}:{h['line_no']} — {s}")
    if len(features)>50: out.append(f"- … {len(features)-50} more")

    report = "\n".join(out) + "\n"
    outpath = OUTD/f"geofencing_audit_{ts.replace(':','').replace('-','').replace('T','_').replace('Z','')}.md"
    outpath.write_text(report, encoding="utf-8")

    # Also write a structured JSON for machine use
    j = {"generated_at": ts, "hits": hits, "top_failure_patterns": top_fail}
    (OUTD/"geofencing_audit.json").write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding="utf-8")

    # also write/update a stable 'latest' pointer
latest = OUTD/'geofencing_audit_latest.md'
try:
    latest.write_text(report, encoding='utf-8')
except Exception:
    pass
print(str(outpath))
