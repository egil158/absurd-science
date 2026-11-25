"""Build static, offline-capable GitHub Pages from the CSV source files."""
import csv
import hashlib
import json
from collections import Counter
from html import escape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
COLUMNS = ['field','sub','topic','headline','title','venue','year','url','note','featured_rank']
TOP = '__top20__'
e = lambda value: escape(str(value), quote=True)

def read_cases():
    cases, manifest, urls, ranks, fields = [], [], set(), set(), set()
    for path in sorted((ROOT/'data').glob('*.csv')):
        with path.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != COLUMNS:
                raise ValueError(f'{path.name}: expected columns {COLUMNS}')
            rows = []
            for line, c in enumerate(reader, 2):
                where = f'{path.name}: row {line}'
                if None in c or any(v is None for v in c.values()):
                    raise ValueError(f'{where}: wrong number of columns')
                if not any(c.values()): continue
                if any(not c[k].strip() for k in COLUMNS[:9]):
                    raise ValueError(f'{where}: missing required field')
                if c['field'] == TOP: raise ValueError(f'{where}: reserved field name')
                for key in ['url']:
                    if c[key] and (urlparse(c[key]).scheme not in ('http','https') or not urlparse(c[key]).netloc):
                        raise ValueError(f'{where}: invalid {key}')
                url = c['url'].strip().lower().rstrip('/')
                if url in urls: raise ValueError(f'{where}: duplicate source URL')
                urls.add(url)
                rank = c['featured_rank'].strip()
                if rank:
                    if not rank.isdecimal() or not 1 <= int(rank) <= 20 or int(rank) in ranks:
                        raise ValueError(f'{where}: featured_rank must be a unique integer 1–20')
                    ranks.add(int(rank)); c['featured_rank'] = int(rank)
                else: c['featured_rank'] = 0
                rows.append(c)
            if len(rows) > 1000: raise ValueError(f'{path.name}: maximum 1000 papers per field')
            if not rows: continue
            field = rows[0]['field']
            if field in fields or any(c['field'] != field for c in rows):
                raise ValueError(f'{path.name}: use one unique field per CSV')
            fields.add(field); cases.extend(rows)
            manifest.append({'file': 'data/'+path.name,'field':field,'count':len(rows)})
    if not cases: raise ValueError('No cases in data/*.csv')
    if len(ranks) != 20: print(f'Warning: {len(ranks)} of 20 featured ranks assigned')
    return cases, manifest

def anchor(case):
    return 'paper-' + hashlib.sha256(case['url'].encode()).hexdigest()[:12]

def render(case):
    fields = {k: e(v) for k,v in case.items()}
    return ('<li id="{anchor}" class="entry" data-field="{field}" data-sub="{sub}" data-topic="{topic}" data-rank="{featured_rank}" data-title="{title}">'
            '<a href="{url}" target="_blank" rel="noopener noreferrer">{headline}</a><span class="venue">{venue}</span></li>').format(**fields, anchor=anchor(case))

def button(field, name, n):
    return f'<button type="button" class="group" data-field="{e(field)}">{e(name)} <small>{n}</small></button>'

def main():
    cases, manifest = read_cases()
    counts = Counter(c['field'] for c in cases)
    featured = sorted((c for c in cases if c['featured_rank']),key=lambda c:c['featured_rank'])
    ordered = featured + [c for c in cases if not c['featured_rank']]
    replacements = {
        '__TOTAL__': str(len(cases)), '__FIELDS__': str(len(counts)), '__FEATURE_COUNT__': str(len(featured)),
        '__CARDS__': '\n'.join(map(render,ordered)),
        '__BUTTONS__': button(TOP,'Top 20',len(featured)) + button('', 'All fields',len(cases)) + ''.join(button(f,f,n) for f,n in counts.items()),
        '__FEATURES__': ''.join(f'<a href="#{anchor(c)}">{e(c["headline"])}<span>{e(c["venue"])} · {e(c["year"])}</span></a>' for c in featured[:3]),
        '__DOWNLOADS__': ''.join(f'<a href="{e(m["file"])}" download>{e(m["field"])} CSV</a>' for m in manifest)
    }
    html = (ROOT/'page.tmpl').read_text(encoding='utf-8')
    for key,value in replacements.items(): html = html.replace(key,value)
    (ROOT/'index.html').write_text(html,encoding='utf-8')
    (ROOT/'data'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Built {len(cases)} cases, {len(counts)} fields, {len(featured)} featured')

if __name__ == '__main__': main()
