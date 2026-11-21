#!/usr/bin/env python3
"""code-tools locate: issue text -> the few source files/lines most likely to need the change.
Ensemble of three cheap signals, fused by reciprocal rank: (1) exact identifiers, quoted strings and paths from the
issue found with `git grep -F`, weighted by rarity; (2) definitions (def/class) of those identifiers; (3) the test
files that mention them (their imports point at the owning module). Stdlib only, offline, ~1-3 s, output <= 4000 chars."""
import argparse, collections, math, os, re, subprocess, sys

TEST = re.compile(r'(^|/)(tests?|testing)/|(^|/)test_[^/]*\.py$|_test\.py$|(^|/)conftest\.py$')
STOP = set('''self none true false return import class def from print list dict str int float bool type object value values data
name names path file files test tests error errors issue example result results default args kwargs option options this that with
when should would could expected actual instead using used call called function method module python string number param params'''.split())

def sh(args, root):
    try: return subprocess.run(args, cwd=root, capture_output=True, text=True, timeout=20).stdout
    except Exception: return ''

def root_dir(r):
    for c in [r, '/workspace', os.getcwd()]:
        if c and os.path.isdir(os.path.join(c, '.git')): return c
    return r or os.getcwd()

def keys(issue):
    k = collections.OrderedDict()
    for m in re.findall(r'`([^`\n]{2,80})`', issue): k[m.strip()] = 3.0                       # code spans
    for m in re.findall(r'''["']([^"'\n]{8,80})["']''', issue): k.setdefault(m.strip(), 2.5)  # messages
    for m in re.findall(r'[\w./-]+\.(?:py|pyi|toml|cfg|ini|json|yaml|yml|md|rst|txt)\b', issue): k[m] = 4.0
    for m in re.findall(r'\b[A-Za-z_][\w]*(?:\.[A-Za-z_]\w*)+\b', issue): k.setdefault(m, 2.0)  # a.b.c
    for m in re.findall(r'\b(?:[a-z]+_[a-z0-9_]+|[A-Z][a-z0-9]+[A-Z]\w*|[a-z]+[A-Z]\w*)\b', issue): k.setdefault(m, 1.5)
    for m in re.findall(r'\b[A-Za-z_]\w{3,}\b', issue):
        if m.lower() not in STOP: k.setdefault(m, 0.5)
    out = []
    for s, w in k.items():
        s = s.strip('().,:; ')
        if len(s) >= 3 and s.lower() not in STOP: out.append((s, w))
    return out[:60]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--issue', default=''); ap.add_argument('--issue-file', default='')
    ap.add_argument('--k', type=int, default=6); ap.add_argument('--root', default='')
    a = ap.parse_args()
    issue = a.issue or (open(a.issue_file).read() if a.issue_file else sys.stdin.read())
    root = root_dir(a.root)
    tracked = [f for f in sh(['git', 'ls-files'], root).splitlines()]
    n_files = max(1, len(tracked))
    src_score, test_score, lines, defs = collections.Counter(), collections.Counter(), collections.defaultdict(list), {}
    for kw, w in keys(issue):
        if '/' in kw or re.search(r'\.(py|toml|cfg|ini|json|ya?ml|md|rst|txt)$', kw):
            for f in tracked:
                if f.endswith(kw.lstrip('./')) or f.endswith('/' + kw.split('/')[-1]): src_score[f] += w * 3
            continue
        leaf = kw.split('.')[-1] if '.' in kw and ' ' not in kw else kw
        out = sh(['git', 'grep', '-n', '-I', '-F', '--max-count=8', '-e', leaf, '--', '*.py', '*.pyi'], root).splitlines()
        hit_files = {l.split(':', 1)[0] for l in out}
        if not hit_files or len(hit_files) > 0.3 * n_files + 25: continue
        idf = math.log(1 + n_files / len(hit_files)) * w
        for l in out:
            f, ln, txt = (l.split(':', 2) + ['', ''])[:3]
            (test_score if TEST.search(f) else src_score)[f] += idf / (1 + 0.25 * len(lines[f]))
            is_def = re.match(r'\s*(async\s+def|def|class)\s+' + re.escape(leaf) + r'\b', txt)
            if is_def: defs[(f, ln)] = txt.strip()[:110]; src_score[f] += 2 * idf
            if len(lines[f]) < 4 and all(x[0] != int(ln or 0) for x in lines[f]): lines[f].append((int(ln) if ln.isdigit() else 0, txt.strip()[:110], bool(is_def)))
    # tests vote for the modules they import
    for t, s in test_score.most_common(8):
        for imp in re.findall(r'^\s*(?:from|import)\s+([\w.]+)', sh(['git', 'show', 'HEAD:' + t], root), re.M)[:40]:
            p = imp.replace('.', '/')
            for f in src_score:
                if f.endswith(p + '.py') or f.endswith(p + '/__init__.py'): src_score[f] += 0.3 * s
    ranked = [f for f, _ in src_score.most_common() if not TEST.search(f)][:a.k]
    if not ranked: print('no confident match; grep the most specific word of the issue with `git grep -n -F "word" -- "*.py" | head -20`'); return
    print('LIKELY FILES (most likely first). Read the listed lines, then edit:')
    for i, f in enumerate(ranked, 1):
        print(f'{i}. {f}  score {src_score[f]:.1f}')
        for ln, txt, d in sorted(lines[f], key=lambda x: (not x[2], x[0]))[:4]: print(f'     {ln}: {"[def] " if d else ""}{txt}')
    tests = [t for t, _ in test_score.most_common(3)]
    if tests: print('TESTS that mention these names (run ONE with `python -m pytest FILE -x -q -k NAME`):', ', '.join(tests))

if __name__ == '__main__':
    try: main()
    except Exception as e: print('locate failed:', repr(e)[:200], '- fall back to git grep -n -F')
