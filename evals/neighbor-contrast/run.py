#!/usr/bin/env python3
"""B1 test: neighbor-contrast pass. A = SKILL.md from git ref (default: main), B = working-tree SKILL.md.
Fixture library: two confusable 'paper' writing skills, a reviewer with a colliding name,
an overclaiming meeting-notes skill, and an unrelated control.
Usage: python3 run.py [N=3] [model=sonnet] [base_ref=main]   (needs the claude CLI)"""
import os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.join(here, '..', '..')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
MODEL = sys.argv[2] if len(sys.argv) > 2 else 'sonnet'
REF = sys.argv[3] if len(sys.argv) > 3 else 'main'
variants = {'A': subprocess.run(['git', '-C', root, 'show', f'{REF}:SKILL.md'], capture_output=True, text=True).stdout,
            'B': open(os.path.join(root, 'SKILL.md')).read()}
lib = os.path.join(here, 'library')
files = sorted(os.listdir(lib))
prompt = ('Run barber\'s library-wide tune-up on these installed skills. Bodies are included. '
          'Report per barber\'s format; one line per finding.\n\n' +
          '\n\n'.join(f'<skill file="{f}">\n' + open(os.path.join(lib, f)).read() + '\n</skill>' for f in files))

def ask(args):
    var, i = args
    out = subprocess.run(['claude', '-p', prompt, '--model', MODEL, '--tools', '',
                          '--append-system-prompt', variants[var]],
                         capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=600).stdout
    return var, i, out

def has(out, *pats):
    return any(all(re.search(p, l, re.I) for p in pats) for l in out.split('\n'))

CHECKS = {
  'pairs paper-writing with academic-paper-writer': lambda o: has(o, r'paper-writing', r'academic-paper-writer'),
  'proposes a "Not for:" exclusion': lambda o: bool(re.search(r'Not for:', o)),
  'flags name collision (paper-*)': lambda o: has(o, r'(name|collid|collision|prefix|first word|qualifier)', r'paper-(writing|review)'),
  'catches meeting-notes overclaim (Jira/Slack/email)': lambda o: has(o, r'meeting-notes', r'(overclaim|not supported|body (does not|doesn.t)|no (jira|slack))'),
  'control (git-commit-messages) not paired as confusable': lambda o: not has(o, r'git-commit-messages', r'(overlap|confus|collid|collision|neighbor)'),
}
jobs = [(v, i) for v in variants for i in range(N)]
with ThreadPoolExecutor(6) as ex:
    results = list(ex.map(ask, jobs))
os.makedirs(os.path.join(here, 'out'), exist_ok=True)
tally = {v: {k: 0 for k in CHECKS} for v in variants}
for var, i, out in results:
    open(os.path.join(here, 'out', f'{var}-{i}.txt'), 'w').write(out)
    for k, f in CHECKS.items(): tally[var][k] += bool(f(out))
print(f'model={MODEL} runs/variant={N} base={REF}')
for v in variants:
    print(f' variant {v}:')
    for k, n in tally[v].items(): print(f'   {n}/{N}  {k}')
