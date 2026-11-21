"""Bounded, read-only localization: BM25 query views with reciprocal-rank fusion."""
import argparse
import ast
import math
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

SKIP = {'.git', '.venv', 'venv', 'env', 'build', 'dist', 'node_modules',
        '__pycache__', '.tox', '.eggs', 'site-packages'}
STOP = set('a an and are as at be by can could do does for from has have how if in into is it its may might '
           'must no not of on or should so than that the then this to use used uses using was were when which while '
           'will with would you your we our issue bug fix fixed fixes feature add adds added support allow allows '
           'return returns none true false self cls def class import pr pull request description checklist type '
           'changes test tests'.split())
IDENT = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
PART = re.compile(r'[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+')
MAX_FILES, MAX_CHUNKS, MAX_BYTES = 6000, 12000, 32 * 1024**2


def workspace():
    explicit = os.environ.get('SWE_WORKSPACE')
    if explicit and os.path.isdir(explicit):
        return Path(explicit).resolve()
    candidates = [os.getcwd(), '/workspace', os.environ.get('PWD')]
    for candidate in candidates:
        if candidate and os.path.isdir(os.path.join(candidate, '.git')):
            return Path(candidate).resolve()
    return Path('/workspace')


def tokens(text):
    out = []
    for word in IDENT.findall(text):
        low = word.lower()
        if low not in STOP and len(low) > 1:
            out.append(low)
        parts = [p.lower() for p in PART.findall(word)]
        if len(parts) > 1 or '_' in word:
            out.extend(p for p in parts + word.lower().split('_') if len(p) > 2 and p not in STOP)
    return out


def is_test(rel):
    name = rel.rsplit('/', 1)[-1].lower()
    return bool(re.search(r'(^|/)(tests?|testing)/', rel.lower())) or name.startswith('test_') or name.endswith('_test.py') or name == 'conftest.py'


def query_views(query):
    identifiers = re.findall(r'`([A-Za-z_][\w./]*)`', query)
    identifiers += [word for word in IDENT.findall(query)
                    if len(word) >= 4 and ('_' in word or any(c.isupper() for c in word[1:]))]
    identifiers += re.findall(r'\b[\w/]+\.py\b', query)
    identifiers = list(dict.fromkeys(identifiers))[:40]
    literals = [p.strip() for p in re.findall(r'["\']([^"\'\n]{8,100})["\']', query)][:12]
    literals += [line.strip()[:160] for line in query.splitlines()
                 if re.search(r'\b\w*(Error|Exception):', line)][:8]
    # Narrative provides a separate view rather than repeating long reproducer code.
    narrative = re.sub(r'```.*?```', ' ', query, flags=re.S)
    narrative = re.sub(r'`[^`]*`', ' ', narrative)
    behavior = ' '.join(dict.fromkeys(tokens(narrative)))[:1600]
    views = [('issue', query, 1.0)]
    if identifiers:
        views.append(('identifiers', ' '.join(identifiers), 1.4))
    if literals:
        views.append(('errors', ' '.join(literals), 1.2))
    if behavior:
        views.append(('behavior', behavior, 1.0))
    return views, identifiers, literals


def index_source(root, deadline):
    chunks, count, total, limited, skipped = [], 0, 0, False, 0
    if not root.is_dir():
        return chunks, {'files': 0, 'limited': False, 'skipped': 0}
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not d.startswith('.')
                         and not os.path.islink(os.path.join(directory, d)))
        for filename in sorted(files):
            if time.monotonic() >= deadline or count >= MAX_FILES or len(chunks) >= MAX_CHUNKS or total >= MAX_BYTES:
                limited = True
                break
            if not filename.endswith('.py') or filename.startswith('.'):
                continue
            path = Path(directory) / filename
            rel = path.relative_to(root).as_posix()
            if is_test(rel) or path.is_symlink():
                continue
            try:
                size = path.stat().st_size
                if size > 400000 or total + size > MAX_BYTES:
                    skipped += 1
                    continue
                source = path.read_text(encoding='utf-8', errors='replace')
                tree = ast.parse(source)
            except (OSError, SyntaxError, ValueError, RecursionError):
                skipped += 1
                continue
            count += 1
            total += size
            lines = source.splitlines()
            before = len(chunks)

            def visit(node, prefix=''):
                for child in ast.iter_child_nodes(node):
                    if len(chunks) >= MAX_CHUNKS:
                        return
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        name = prefix + child.name
                        start, end = child.lineno, getattr(child, 'end_lineno', child.lineno)
                        body = '\n'.join(lines[start - 1:min(end, start + 120)])[:8000]
                        chunks.append((rel, start, end, 'class' if isinstance(child, ast.ClassDef) else 'def', name, body))
                        if isinstance(child, ast.ClassDef):
                            visit(child, name + '.')
            visit(tree)
            if len(chunks) == before:
                chunks.append((rel, 1, len(lines), 'module', rel, source[:8000]))
        if limited:
            break
    return chunks, {'files': count, 'limited': limited, 'skipped': skipped}


def rank(chunks, query, mode='evidence'):
    views, exact, literals = query_views(query)
    if mode == 'legacy':
        views = views[:1]
    docs, df = [], Counter()
    for rel, start, end, kind, name, body in chunks:
        terms = tokens(name) * 3 + tokens(rel) * 2 + tokens(body)
        counts = Counter(terms)
        docs.append((counts, len(terms)))
        df.update(counts.keys())
    if not docs:
        return [], {}
    avg = max(1.0, sum(length for _, length in docs) / len(docs))
    fused, evidence = Counter(), {}
    for label, text, weight in views:
        query_counts = Counter(dict(Counter(tokens(text)).most_common(128)))
        scores = []
        for i, ((counts, length), chunk) in enumerate(zip(docs, chunks)):
            rel, start, end, kind, name, body = chunk
            score = 0.0
            for term, qf in query_counts.items():
                tf = counts.get(term, 0)
                if tf:
                    idf = math.log(1 + (len(docs) - df[term] + 0.5) / (df[term] + 0.5))
                    score += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * length / avg)) * min(qf, 3)
            if label in ('issue', 'identifiers'):
                if name in exact or name.rsplit('.', 1)[-1] in exact:
                    score += 12
                elif any(word in body for word in exact):
                    score += 3
                if any(rel == word or rel.endswith('/' + word) for word in exact):
                    score += 12
            if label in ('issue', 'errors'):
                score += sum(6 for phrase in literals if phrase in body)
            if rel.startswith(('docs/', 'docs_src/', 'scripts/', 'examples/')):
                score *= 0.6
            if score > 0:
                scores.append((score, i))
        scores.sort(key=lambda pair: (-pair[0], chunks[pair[1]][0], chunks[pair[1]][1], chunks[pair[1]][4]))
        for position, (score, i) in enumerate(scores[:60], 1):
            fused[i] += weight / (60 + position) if mode != 'legacy' else score
            evidence.setdefault(i, []).append(f'{label}#{position}')
    if mode != 'legacy':
        # A missing narrative match must not erase an explicit symbol match.
        for i in list(fused):
            rel, start, end, kind, name, body = chunks[i]
            if name in exact or name.rsplit('.', 1)[-1] in exact:
                fused[i] += 0.035
                evidence[i].append('exact-symbol')
            elif any(rel == word or rel.endswith('/' + word) for word in exact):
                fused[i] += 0.02
                evidence[i].append('exact-file')
    indices = sorted(fused, key=lambda i: (-fused[i], chunks[i][0], chunks[i][1], chunks[i][4]))
    return indices, evidence


def snippet(chunk, query):
    rel, start, end, kind, name, body = chunk
    needles = set(tokens(query))
    lines = body.splitlines()
    chosen = [i for i, line in enumerate(lines) if needles.intersection(tokens(line))][:2] or [0]
    return [f'    {start + i}: {lines[i].strip()[:150]}' for i in chosen if i < len(lines)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', default='')
    parser.add_argument('--top', type=int, default=8)
    parser.add_argument('--seconds', type=float, default=8)
    parser.add_argument('--mode', choices=['evidence', 'legacy'], default='evidence')
    parser.add_argument('rest', nargs='*')
    opts, extra = parser.parse_known_args()
    query = ' '.join([opts.query, *opts.rest, *[s for s in extra if not s.startswith('--')]])[:6000].strip()
    if not query:
        print('Pass the issue title, identifiers or error text with option query.')
        return
    started = time.monotonic()
    chunks, stats = index_source(workspace(), started + max(0.1, min(opts.seconds, 12)))
    try:
        indices, evidence = rank(chunks, query, opts.mode)
        selected_mode = opts.mode
    except (ValueError, ArithmeticError, RecursionError) as error:
        print(f'Evidence ranking failed ({type(error).__name__}); using issue-only lexical fallback.')
        indices, evidence = rank(chunks, query, 'legacy')
        selected_mode = 'legacy'
    if not indices:
        print('No source matches. Use exact identifiers with run_command or search_similar_code; do not guess.')
        return
    top = indices[:max(1, min(opts.top, 10))]
    print(f'Evidence Scout | mode={selected_mode} | {stats["files"]} files, {len(chunks)} symbols | limited={stats["limited"]}')
    print('Ranked locations (retrieval evidence; ranks are not confidence probabilities):')
    output = []
    for position, i in enumerate(top, 1):
        rel, start, end, kind, name, body = chunks[i]
        output.append(f'  {position}. {rel}:{start}-{end} {kind} {name} | ' + ', '.join(evidence[i]))
        output.extend(snippet(chunks[i], query))
    files = list(dict.fromkeys(chunks[i][0] for i in indices))[:5]
    output.append('Most relevant files: ' + ' | '.join(files))
    output.append('Next: reread the exact source and confirm the cause before editing. No match is not proof of absence.')
    print('\n'.join(output)[:5800])


if __name__ == '__main__':
    main()
