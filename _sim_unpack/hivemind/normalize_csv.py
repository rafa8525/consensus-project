import csv, sys, re, pathlib
src = pathlib.Path(sys.argv[1]); dst = pathlib.Path(sys.argv[2])
with src.open(encoding='utf-8-sig', newline='') as f:
    r = csv.DictReader(f)
    def norm(s): return re.sub(r'[^a-z0-9]+','', (s or '').lower())
    mapping = {}
    for name in r.fieldnames or []:
        k = norm(name)
        if k in ('agent','agentname','name','persona'): mapping['Agent']=name
        elif k in ('focus','focusarea','specialty'): mapping['Focus']=name
        elif k in ('role','function','archetype','job'): mapping['Role']=name
        elif k in ('supportsite','site','url','link'): mapping['SupportSite']=name
    need = {'Agent','Focus','Role','SupportSite'}
    missing = need - mapping.keys()
    if missing:
        print("Missing columns:", missing, "\nFound headers:", r.fieldnames); sys.exit(2)
    rows=[{k:(row.get(mapping[k],'') or '').strip() for k in need} for row in r]
with dst.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['Agent','Focus','Role','SupportSite'])
    w.writeheader(); w.writerows(rows)
print("Wrote", dst)
