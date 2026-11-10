#!/usr/bin/env python3
"""B3 test: library-size warning. Builds a synthetic library (default 120 skills, descriptions only),
runs the tune-up with A = SKILL.md from git ref (default main), B = working tree, and checks the report
for the size warning and both recommendations. Control: 30-skill library must NOT get the warning.
Usage: python3 run.py [N=3] [model=sonnet] [base_ref=main]"""
import os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.join(here, '..', '..')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
MODEL = sys.argv[2] if len(sys.argv) > 2 else 'sonnet'
REF = sys.argv[3] if len(sys.argv) > 3 else 'main'
variants = {'A': subprocess.run(['git', '-C', root, 'show', f'{REF}:SKILL.md'], capture_output=True, text=True).stdout,
            'B': open(os.path.join(root, 'SKILL.md')).read()}
TOPICS = ['invoice', 'recipe', 'sql', 'kubernetes', 'resume', 'poetry', 'tax', 'chess', 'terraform', 'podcast']
def library(n):
    out = []
    for i in range(n):
        t = TOPICS[i % len(TOPICS)]
        out.append(f'- name: {t}-helper-{i:03d}\n  description: "Helps with {t} tasks #{i}. Use whenever the user mentions {t}."')
    return '\n'.join(out)
def prompt(n):
    return f'Run barber\'s library-wide tune-up. Installed skills ({n} total, descriptions only):\n\n' + library(n)
def ask(a):
    v, n, i = a
    return v, n, i, subprocess.run(['claude', '-p', prompt(n), '--model', MODEL, '--tools', '',
        '--append-system-prompt', variants[v]], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=600).stdout
CHECKS = {
  'size warning (count + suppress/recall)': lambda o: bool(re.search(r'\b120\b', o)) and bool(re.search(r'recall|suppress|crowd|dilut|fewer|loading', o, re.I)),
  'recommends disabling unused skills': lambda o: bool(re.search(r'disabl|remov|uninstall', o, re.I)) and bool(re.search(r'unused', o, re.I)),
  'recommends preselecting skills at scale': lambda o: bool(re.search(r'preselect|pre-select|select(ing)? .{0,30}before', o, re.I)),
  'notes task success hides it': lambda o: bool(re.search(r'work(s)? around|hides|mask|hidden|look(s)? like it works|still losing', o, re.I)),
}
jobs = [(v, 120, i) for v in variants for i in range(N)] + [('B', 30, i) for i in range(N)]
with ThreadPoolExecutor(6) as ex: results = list(ex.map(ask, jobs))
os.makedirs(os.path.join(here, 'out'), exist_ok=True)
tally = {v: {k: 0 for k in CHECKS} for v in variants}; ctrl = 0
for v, n, i, o in results:
    open(os.path.join(here, 'out', f'{v}-{n}-{i}.txt'), 'w').write(o)
    if n == 120:
        for k, f in CHECKS.items(): tally[v][k] += bool(f(o))
    else: ctrl += bool(re.search(r'suppress|past (the )?~?100|over (the )?~?100|above (the )?~?100', o, re.I))
print(f'model={MODEL} runs/variant={N} base={REF} library=120 skills')
for v in variants:
    print(f' variant {v}:')
    for k, c in tally[v].items(): print(f'   {c}/{N}  {k}')
print(f' control (B, 30 skills) runs showing the warning: {ctrl}/{N}  (want 0)')
