#!/usr/bin/env python3
"""A/B test: does the contradiction bullet make barber catch planted conflicts?
Variant A = barber SKILL.md as-is. Variant B = SKILL.md + bullet.txt inserted after the
'Repetition?' bullet in section 2. Each cell runs N times via headless `claude -p`.
Usage: python3 run.py [N=3] [model=sonnet]   (needs the claude CLI)"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
MODEL = sys.argv[2] if len(sys.argv) > 2 else 'sonnet'
skill = open(os.path.join(here, '..', '..', 'SKILL.md')).read()
bullet = open(os.path.join(here, 'bullet.txt')).read().strip()
anchor = '- Repetition? Same rule stated twice = once.'
assert anchor in skill, 'anchor bullet not found in SKILL.md'
variants = {'A': skill, 'B': skill.replace(anchor, anchor + '\n' + bullet)}
expected = json.load(open(os.path.join(here, 'expected.json')))

def ask(args):
    var, fx, i = args
    text = open(os.path.join(here, fx)).read()
    prompt = ('Audit this skill with barber --check-only. One line per finding.\n\n```\n' + text + '\n```')
    out = subprocess.run(['claude', '-p', prompt, '--model', MODEL, '--tools', '',
                          '--append-system-prompt', variants[var]],
                         capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=300).stdout
    return var, fx, i, out

def found(out, spec):
    for line in out.lower().split('\n'):
        if all(any(k in line for k in grp) for grp in spec['all_of']):
            return True
    return False

jobs = [(v, f, i) for v in variants for f in expected for i in range(N)]
with ThreadPoolExecutor(6) as ex:
    results = list(ex.map(ask, jobs))
os.makedirs(os.path.join(here, 'out'), exist_ok=True)
tally = {}
for var, fx, i, out in results:
    open(os.path.join(here, 'out', f'{var}-{fx}-{i}.txt'), 'w').write(out)
    t = tally.setdefault((var, fx), {'hits': 0, 'chances': 0, 'fp': 0})
    for spec in expected[fx]['planted']:
        t['chances'] += 1
        t['hits'] += found(out, spec)
    if not expected[fx]['planted']:
        flagged = [l for l in out.lower().split('\n')
                   if re.search(r'contradict|conflict', l) and not re.search(r'\bno\b|none|not a', l)]
        t['fp'] += bool(flagged)
print(f'model={MODEL} runs/cell={N}')
for (var, fx), t in sorted(tally.items()):
    if expected[fx]['planted']:
        print(f'  {var} {fx}: caught {t["hits"]}/{t["chances"]} planted contradictions')
    else:
        print(f'  {var} {fx}: runs with a contradiction finding on a clean skill: {t["fp"]}/{N}')
