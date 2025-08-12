#!/usr/bin/env python3
import os, re, json, hashlib, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEM  = ROOT / "memory"
IDX_DIR = MEM / "index"
LOG_DIR = MEM / "logs" / "heartbeat"
IDX_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

IGNORE_DIRS = {
    ".git", "__pycache__", "archive", "github_sync"
}
IGNORE_PATTERNS = [
    r".*\.zip$", r".*\.gz$", r".*\.pdf$", r".*\.png$", r".*\.jpg$", r".*\.jpeg$", r".*\.webp$"
]
MAX_FILE_BYTES = 5_000_000  # 5MB content cap for keyword scan (index still records larger files)

def want(path: Path) -> bool:
    rel = path.relative_to(MEM)
    parts = set(rel.parts)
    if any(p in IGNORE_DIRS for p in parts): return False
    s = str(rel)
    if "logs/heartbeat/full_memory_absorption.log" in s: return False
    for pat in IGNORE_PATTERNS:
        if re.match(pat, s, flags=re.I): return False
    return True

def sha1_file(p: Path, limit=None):
    h = hashlib.sha1()
    with p.open("rb") as f:
        if limit:
            remaining = limit
            while remaining > 0:
                chunk = f.read(min(1024*1024, remaining))
                if not chunk: break
                h.update(chunk); remaining -= len(chunk)
        else:
            for chunk in iter(lambda: f.read(1024*1024), b""):
                h.update(chunk)
    return h.hexdigest()

def extract_text(p: Path, max_bytes=MAX_FILE_BYTES):
    try:
        b = p.read_bytes()
        if len(b) > max_bytes: b = b[:max_bytes]
        try:
            return b.decode("utf-8", errors="ignore")
        except Exception:
            return ""
    except Exception:
        return ""

def keywords(txt: str, top=20):
    tokens = re.findall(r"[A-Za-z0-9_]{3,}", txt.lower())
    stop = set(("the","and","for","with","not","you","this","that","have","are","from","your","about",
                "into","was","were","will","would","could","should","they","them","their","then","than",
                "over","under","between","again","able","also","just","like","into","onto","upon"))
    freq = {}
    for t in tokens:
        if t in stop: continue
        freq[t] = freq.get(t,0)+1
    return sorted(freq, key=freq.get, reverse=True)[:top]

def main():
    t0 = time.time()
    manifest = []
    for p in MEM.rglob("*"):
        if not p.is_file(): continue
        if not want(p): continue
        rel = p.relative_to(MEM).as_posix()
        st = p.stat()
        item = {
            "path": rel,
            "size": st.st_size,
            "mtime": int(st.st_mtime),
            "sha1": sha1_file(p, limit=min(st.st_size, 2_000_000)),  # partial hash for speed
        }
        # light-weight keywords for text-ish files
        if st.st_size <= MAX_FILE_BYTES and re.search(r"\.(txt|md|json|py|sh|log)$", rel, re.I):
            txt = extract_text(p)
            item["title"] = (txt.splitlines()[0][:120] if txt else "")
            item["keywords"] = keywords(txt)
        manifest.append(item)

    manifest.sort(key=lambda x: x["path"])
    out = {
        "generated_at": int(time.time()),
        "total_files": len(manifest),
        "manifest": manifest,
    }
    (IDX_DIR / "search_index.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

    # Write/append heartbeat
    hb = LOG_DIR / "memory_absorption_heartbeat.log"
    elapsed = round(time.time()-t0, 2)
    hb.write_text("", encoding="utf-8") if not hb.exists() else None
    with hb.open("a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] indexed={len(manifest)} elapsed={elapsed}s\n")

if __name__ == "__main__":
    main()
