import csv, sys, re, pathlib

src = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])

def norm(s): return re.sub(r'[^a-z0-9]+','', (s or '').lower())

# Known header aliases -> canonical
ALIASES = {
    'agent': {'agent','agentname','name','persona','agent#','agentnumber'},
    'focus': {'focus','focusarea','specialty','dailyrepairfocus','repairfocus'},
    'role':  {'role','function','archetype','job','proposedupgradedrole','upgradedrole'},
    'site':  {'supportsite','site','url','link','primarysupportsite','supporturl'},
}

def classify(header: str):
    h = norm(header)
    for canon, names in ALIASES.items():
        if h in names:
            return canon
    # fallback: substring heuristics
    if 'agent' in h: return 'agent'
    if 'focus' in h: return 'focus'
    if 'role'  in h: return 'role'
    if 'support' in h or 'site' in h or 'url' in h or 'link' in h: return 'site'
    return None

with src.open(encoding='utf-8-sig', newline='') as f:
    r = csv.DictReader(f)
    if not r.fieldnames:
        print("No headers found"); sys.exit(2)
    mapping = {}
    for name in r.fieldnames:
        kind = classify(name)
        if kind and kind not in mapping:
            mapping[kind] = name

    need = {'agent','focus','role','site'}
    if not need.issubset(mapping):
        print("Missing columns:", sorted(need - set(mapping)), "\nFound headers:", r.fieldnames)
        sys.exit(2)

    rows=[]
    for row in r:
        rows.append({
            'Agent': (row.get(mapping['agent'], '') or '').strip(),
            'Focus': (row.get(mapping['focus'], '') or '').strip(),
            'Role':  (row.get(mapping['role'],  '') or '').strip(),
            'SupportSite': (row.get(mapping['site'], '') or '').strip(),
        })

with dst.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['Agent','Focus','Role','SupportSite'])
    w.writeheader(); w.writerows(rows)
print("Wrote", dst)
