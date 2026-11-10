#!/usr/bin/env python3
"""Static scores for SKILL.md files (SkillCT-style, arXiv 2610.38147). Python stdlib only.

Usage: python3 scripts/skill_scores.py [--json] SKILL.md [SKILL.md ...]

Conciseness (body = everything after frontmatter):
  lines, empty_ratio, repeated_ratio, unique_density, score 0-100
Description-body consistency:
  keyword_cov, bigram_cov, tfidf_cos, title_cov, score 0-100
Scores are relative signals for ranking skills, not absolute grades.
"""
import json, math, re, sys
from collections import Counter

STOP = set("""a an and are as at be but by can do for from has have how if in into is it its of on or
that the their then there these this to use used uses using was when whenever where which while will with
you your not no all any each per via than also more most such only own same so too very""".split())


def split_skill(text):
    """Return (description, body). Handles quoted, plain, and folded/literal (>, |) descriptions."""
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text, re.S)
    if not m:
        return '', text
    fm, body = m.group(1), m.group(2)
    desc = ''
    lines = fm.split('\n')
    for i, l in enumerate(lines):
        d = re.match(r'^description:\s*(.*)$', l)
        if d:
            val = d.group(1).strip()
            if val in ('>', '|', '>-', '|-', ''):
                parts = []
                for nxt in lines[i + 1:]:
                    if nxt.startswith((' ', '\t')):
                        parts.append(nxt.strip())
                    else:
                        break
                val = ' '.join(parts)
            desc = val.strip('"\'')
            break
    return desc, body


def words(s):
    out = []
    for w in re.findall(r'[a-z][a-z0-9_-]{2,}', s.lower()):
        if w in STOP:
            continue
        if len(w) > 4 and w.endswith('s') and not w.endswith('ss'):
            w = w[:-1]
        out.append(w)
    return out


def bigrams(ws):
    return set(zip(ws, ws[1:]))


def tfidf_cos(desc_ws, body_ws):
    """Cosine of tf-idf vectors; idf over {description} + body paragraphs/lines as documents."""
    docs = [Counter(desc_ws)]
    chunk = []
    for w in body_ws:
        chunk.append(w)
        if len(chunk) == 20:
            docs.append(Counter(chunk)); chunk = []
    if chunk:
        docs.append(Counter(chunk))
    n = len(docs)
    df = Counter()
    for d in docs:
        df.update(d.keys())
    idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
    def vec(c):
        return {t: f * idf[t] for t, f in c.items() if t in idf}
    a, b = vec(Counter(desc_ws)), vec(Counter(body_ws))
    num = sum(a[t] * b.get(t, 0) for t in a)
    den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return num / den if den else 0.0


def conciseness(body):
    lines = body.split('\n')
    if lines and lines[-1] == '':
        lines = lines[:-1]
    total = len(lines)
    nonempty = [re.sub(r'\s+', ' ', l.strip().lower()) for l in lines if l.strip()]
    # ignore structural one-liners (fences, rules) when counting repeats
    content = [l for l in nonempty if len(l) > 3]
    repeated = (len(content) - len(set(content))) / len(content) if content else 0.0
    empty = (total - len(nonempty)) / total if total else 0.0
    ws = words(body)
    density = len(set(ws)) / len(ws) if ws else 1.0
    score = 100 * (0.4 * (1 - repeated)
                   + 0.3 * min(1.0, density / 0.6)
                   + 0.2 * (1 - min(1.0, max(0.0, empty - 0.25) / 0.5))
                   + 0.1 * (1 - min(1.0, total / 500)))
    return {'lines': total, 'empty_ratio': round(empty, 3), 'repeated_ratio': round(repeated, 3),
            'unique_density': round(density, 3), 'score': round(score, 1)}


def consistency(desc, body):
    dw, bw = words(desc), words(body)
    if not dw or not bw:
        return {'keyword_cov': 0.0, 'bigram_cov': 0.0, 'tfidf_cos': 0.0, 'title_cov': 0.0, 'score': 0.0}
    bset = set(bw)
    kw = sum(1 for w in set(dw) if w in bset) / len(set(dw))
    db, bb = bigrams(dw), bigrams(bw)
    bg = len(db & bb) / len(db) if db else 0.0
    cos = tfidf_cos(dw, bw)
    titles = re.findall(r'^#{1,6}\s+(.+?)\s*$', body, re.M)
    dset = set(dw)
    tc = (sum(1 for t in titles if set(words(t)) & dset) / len(titles)) if titles else 0.0
    score = 100 * (kw + bg + cos + tc) / 4
    return {'keyword_cov': round(kw, 3), 'bigram_cov': round(bg, 3), 'tfidf_cos': round(cos, 3),
            'title_cov': round(tc, 3), 'score': round(score, 1)}


def score_text(text):
    desc, body = split_skill(text)
    return {'description_found': bool(desc), 'conciseness': conciseness(body), 'consistency': consistency(desc, body)}


def score_file(path):
    with open(path, encoding='utf-8') as f:
        r = score_text(f.read())
    r['file'] = path
    return r


def main(argv):
    as_json = '--json' in argv
    paths = [a for a in argv if not a.startswith('--')]
    if not paths:
        print(__doc__); return 2
    results = [score_file(p) for p in paths]
    if as_json:
        print(json.dumps(results, indent=2)); return 0
    for r in results:
        c, k = r['conciseness'], r['consistency']
        print(f"{r['file']}")
        print(f"  conciseness {c['score']:5.1f}  lines={c['lines']} empty={c['empty_ratio']} repeated={c['repeated_ratio']} unique_density={c['unique_density']}")
        note = '' if r['description_found'] else '  (no description found)'
        print(f"  consistency {k['score']:5.1f}  keyword={k['keyword_cov']} bigram={k['bigram_cov']} tfidf_cos={k['tfidf_cos']} title={k['title_cov']}{note}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
