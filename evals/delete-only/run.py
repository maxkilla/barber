#!/usr/bin/env python3
"""B5 test: full audit on a fat fixture, then verify every body edit is a deletion and every kept line unchanged.
A = SKILL.md from git ref (default main), B = working tree. Each run is told to apply ALL its proposed
cuts and print the complete edited SKILL.md in one fenced block (tools disabled; edits are simulated in text).
Checks per run: (1) edited file parsed; (2) every non-frontmatter sentence of the edit exists verbatim in the original
(deleting whole sentences is fine, changing any is a reword); (3) the Safety line survives; (4) body got shorter.
Usage: python3 run.py [N=3] [model=sonnet] [base_ref=main]"""
import os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.join(here, '..', '..')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
MODEL = sys.argv[2] if len(sys.argv) > 2 else 'sonnet'
REF = sys.argv[3] if len(sys.argv) > 3 else 'main'
variants = {'A': subprocess.run(['git', '-C', root, 'show', f'{REF}:SKILL.md'], capture_output=True, text=True).stdout,
            'B': open(os.path.join(root, 'SKILL.md')).read()}
orig = open(os.path.join(here, 'fixtures', 'fat.md')).read()
prompt = ('Run a full barber audit of this skill and apply every cut you would propose (assume the user approved all findings). '
          'Then output the complete edited SKILL.md in ONE fenced block labelled ```markdown, and nothing else inside that block.\n\n```\n' + orig + '\n```')

def split(t):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', t, re.S)
    return (m.group(1), m.group(2)) if m else ('', t)
def ask(a):
    v, i = a
    return v, i, subprocess.run(['claude', '-p', prompt, '--model', MODEL, '--tools', '',
        '--append-system-prompt', variants[v]], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=600).stdout
def edited(o):
    blocks = re.findall(r'```markdown\n(.*?)\n```', o, re.S)
    return blocks[-1] if blocks else None
def score(o):
    e = edited(o)
    if not e: return dict(parsed=False, verbatim=False, safety=False, shorter=False, rewords=[])
    _, ob = split(orig); _, eb = split(e)
    sents = lambda t: [x.strip() for l in t.split('\n') for x in re.split(r'(?<=[.!?])\s+', l.strip()) if x.strip()]
    okset = set(sents(ob))  # sentence-level: deleting a sentence from a line is allowed, changing one is not
    rewords = [x for x in sents(eb) if x not in okset]
    return dict(parsed=True, verbatim=not rewords, safety='Never send a report to external recipients' in eb,
                shorter=len([l for l in eb.split('\n') if l.strip()]) < len([l for l in ob.split('\n') if l.strip()]), rewords=rewords)
jobs = [(v, i) for v in variants for i in range(N)]
with ThreadPoolExecutor(6) as ex: results = list(ex.map(ask, jobs))
os.makedirs(os.path.join(here, 'out'), exist_ok=True)
agg = {v: dict(parsed=0, verbatim=0, safety=0, shorter=0) for v in variants}; ex_r = {}
for v, i, o in results:
    open(os.path.join(here, 'out', f'{v}-{i}.txt'), 'w').write(o)
    s = score(o)
    for k in agg[v]: agg[v][k] += bool(s[k])
    if s['rewords']: ex_r.setdefault(v, s['rewords'][:2])
print(f'model={MODEL} runs/variant={N} base={REF}')
for v in variants:
    a = agg[v]
    print(f' variant {v}: parsed {a["parsed"]}/{N}  body-sentences-all-verbatim {a["verbatim"]}/{N}  safety-kept {a["safety"]}/{N}  shorter {a["shorter"]}/{N}')
    for r in ex_r.get(v, []): print('    reworded line example:', r[:100])
