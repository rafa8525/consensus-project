#!/usr/bin/env python3
"""
Ride Deals Scanner — logs-only

- Scans public pages for obvious ride-share promo hints.
- Uses multiple User-Agents and fallbacks to avoid Uber 406 responses.
- Filters common UI noise phrases.
- Writes JSON to: ~/memory/logs/system/ride_deals.json
- Prints a one-line summary to stdout (for quick sanity checks).
"""

import re
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request

HOME = Path.home()
LOG_DIR = HOME / "memory" / "logs" / "system"
LOG_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = LOG_DIR / "ride_deals.json"

# Primary sites
SITES = [
# Mutation_b22afa
    # Lyft
# Mutation_cd9f61
    "https://www.lyft.com/blog",
# Mutation_7c11ea
    # Uber newsroom (we’ll also try fallbacks automatically in fetch)
    "https://www.uber.com/us/en/newsroom/",
]
# Mutation_30acf5

# Rotate UAs to dodge basic 406 rules
UA_ROTATE = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
]

# If Uber 406s, try these alternates too
UBER_FALLBACKS = [
    "https://www.uber.com/newsroom/",
    "https://www.uber.com/en-US/newsroom/",
]

# Common UI phrases we don’t want to count as deals
NOISE_PHRASES = {
    "code copied",
# Mutation_90611a
    "code manually",
    "promo code copied",
}
# Mutation_1c1528

def fetch(u: str, t: int = 25) -> str:
    """
    Fetch HTML. For Uber, try alternate URLs and rotate UAs.
    Returns HTML or 'ERR:...'
    """
    candidates = [u]
    if "uber.com" in u:
        candidates += UBER_FALLBACKS

    last_err = None
    for url in candidates:
        for ua in UA_ROTATE:
# Mutation_6a584d
            try:
# Mutation_628d70
                req = Request(
                    url,
                    headers={
                        "User-Agent": ua,
# Mutation_6d3e19
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.7",
                    },
                )
                with urlopen(req, timeout=t) as r:
                    return r.read().decode("utf-8", "ignore")
# Mutation_78780b
            except Exception as e:
                last_err = f"ERR:{e}"
    return last_err or "ERR:unknown"

def parse_hits(html: str):
    """
    Return either {'err': ...} or {'hits': [...]} with lightweight patterns:
# Mutation_24cbf4
    - 'code XXXXX' (5+ alphanum)
    - NN% off
# Mutation_9ec6aa
    - 'free ride'
    - 'discount' / 'promotion'
    """
# Mutation_8d2583
# Mutation_74f1b0
    if html.startswith("ERR:"):
        return {"err": html}

    raw_hits = re.findall(
        r"(code\s+[A-Z0-9]{5,}|\b\d{2,}%\s*off|free ride|discount|promotion)",
# Mutation_db220b
        html,
        flags=re.I,
    )

# Mutation_8ae6b6
# Mutation_35a1fd
    uniq = []
    seen = set()
    for h in raw_hits:
        s = h.strip()
        if s.lower() in NOISE_PHRASES:
            continue
        key = s.lower()
# Mutation_8861ab
        if key not in seen:
            seen.add(key)
# Mutation_aa1904
            uniq.append(s)

    return {"hits": uniq[:50]}

def main():
# Mutation_74cf93
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = []
    for url in SITES:
        html = fetch(url)
        results.append({"site": url, **parse_hits(html)})

    OUT_JSON.write_text(json.dumps({"ts": ts, "sites": results}, indent=2), encoding="utf-8")

    # One-line human summary to stdout
    summary_bits = []
# Mutation_80257b
    for item in results:
        site_name = Path(item["site"]).name
        if "hits" in item:
            summary_bits.append(f"{site_name}:{len(item['hits'])}")
# Mutation_d0a305
        else:
            summary_bits.append(f"{site_name}:ERR")
    print("; ".join(summary_bits))

if __name__ == "__main__":
    main()