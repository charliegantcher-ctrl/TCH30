#!/usr/bin/env python3
"""Turn the ranking doc (markdown) into companies.json for build.py.

Usage: python3 prepare.py "Top 100 tech stocks ranked.md" companies.json
Reads the tier tables (| # | Ticker | Rationale |) and the 12-column metric tables
(Ticker | Company | Category | Period | Rev YoY | Organic | Cust growth | Rev/cust | GP growth | Op margin | FCF | NRR)
and assigns a sign per metric: +1 green, -1 red, 0 grey (not disclosed / not applicable).
"""
import re, json, sys

src = open(sys.argv[1]).read().splitlines()
companies, tiers, why = {}, {}, {}
section, cur_tier = None, None
KEYS = ['ticker', 'name', 'category', 'period', 'rev', 'organic', 'cust', 'revcust', 'gp', 'opm', 'fcf', 'nrr']
FIELDS = KEYS[4:]

for l in src:
    m = re.match(r'### Tier (\d)', l)
    if m:
        cur_tier = int(m.group(1)); continue
    if l.startswith('### '):
        cur_tier, section = None, l[4:].strip(); continue
    if l.startswith('## '):
        cur_tier = None
    if not l.startswith('|') or l.startswith('|---'):
        continue
    cells = [c.strip() for c in l.strip().strip('|').split('|')]
    if cur_tier and len(cells) == 3 and cells[0].isdigit():
        tiers[cells[1]] = (cur_tier, int(cells[0])); why[cells[1]] = cells[2]
    elif len(cells) == 12 and cells[0] != 'Ticker':
        d = dict(zip(KEYS, cells)); d['section'] = section; companies[d['ticker']] = d

def clean(s):
    return re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s).replace('**', '')

def sign(field, s, rev_sign):
    t = s.replace('−', '-').lower()
    if field == 'nrr':
        if 'low-120' in t: return 1
        if t.startswith(('n/d', 'n/a')): return 0
        m = re.search(r'(\d+)\s*%', t)
        return (1 if int(m.group(1)) >= 100 else -1) if m else 0
    if field == 'organic' and t.startswith('~same'):
        return rev_sign
    if field == 'rev' and t.startswith('n/d'):
        return 0
    if field == 'fcf':
        if t.startswith('positive'): return 1
        if 'likely' in t and 'negative' in t: return -1
        if t.startswith('n/d'):
            m = re.search(r'\((?:9m|6m|h1)\s*(?:ocf\s*)?(-?)\s*~?\$', t)
            return (-1 if m.group(1) == '-' else 1) if m else 0
        m = re.search(r'(-?)\s*\$?\s*\d', t)
        return (-1 if m.group(1) == '-' else 1) if m else 0
    if field == 'revcust':
        m = re.search(r'([+\-])\s*\d+(?:\.\d+)?%', t)
        return (1 if m.group(1) == '+' else -1) if m else 0
    if t.startswith(('n/d', 'n/a', 'n/m', 'pre-revenue', 'inorganic', 'not organic', 'mostly acquired',
                     'largely inorganic', '~same')):
        return -1 if 'likely negative' in t else 0
    if 'likely negative' in t: return -1
    m = re.search(r'([+\-])?\s*~?\s*(\d[\d.,]*)\s*%', t)
    if not m:
        m2 = re.search(r'([+\-])\s*\d', t)
        return (1 if m2.group(1) == '+' else -1) if m2 else 0
    if m.group(1) == '-': return -1
    return 1 if float(m.group(2).replace(',', '')) > 0 else 0

out = []
for t, d in companies.items():
    r = {k: clean(v) for k, v in d.items()}
    r['signs'] = {}
    r['signs']['rev'] = sign('rev', r['rev'], 0)
    for f in FIELDS[1:]:
        r['signs'][f] = sign(f, r[f], r['signs']['rev'])
    if t in tiers:
        r['tier'], r['rank'] = tiers[t]; r['why'] = clean(why[t])
    out.append(r)
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print(f"{len(out)} companies, {len(tiers)} ranked", file=sys.stderr)
