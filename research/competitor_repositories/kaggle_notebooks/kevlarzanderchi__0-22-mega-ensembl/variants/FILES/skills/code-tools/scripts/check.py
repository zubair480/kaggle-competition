#!/usr/bin/env python3
"""code-tools check: after an edit, compile every changed .py file, then run the ONE existing test file closest to the
changed module (time-capped). Prints a short PASS/FAIL report and the diff stat. Stdlib only."""
import argparse, os, re, subprocess, sys

def sh(args, root, t=30):
    try: r = subprocess.run(args, cwd=root, capture_output=True, text=True, timeout=t); return r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired: return 124, f'timed out after {t}s'
    except Exception as e: return 1, repr(e)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=''); ap.add_argument('--k', default=''); ap.add_argument('--timeout', type=int, default=90)
    a = ap.parse_args()
    root = next((c for c in [a.root, '/workspace', os.getcwd()] if c and os.path.isdir(os.path.join(c, '.git'))), os.getcwd())
    _, st = sh(['git', 'status', '--porcelain'], root)
    changed = [l[3:].strip() for l in st.splitlines() if l.strip()]
    if not changed: print('NO CHANGES: the working tree is unedited and would score zero. Make your edit now.'); return
    print('changed:', ', '.join(changed[:10]))
    bad = False
    for f in changed:
        if f.endswith('.py') and os.path.isfile(os.path.join(root, f)):
            rc, out = sh([sys.executable, '-m', 'py_compile', f], root)
            if rc: bad = True; print('SYNTAX ERROR', f, out.strip()[-600:])
    if bad: print('fix the syntax error before anything else'); return
    print('compile: ok')
    src = [f for f in changed if f.endswith('.py') and not re.search(r'(^|/)tests?/|test_', f)]
    _, files = sh(['git', 'ls-files', '*.py'], root)
    tests = [t for t in files.splitlines() if re.search(r'(^|/)test_[^/]*\.py$|_test\.py$', t)]
    pick = None
    for f in src:
        stem = os.path.basename(f)[:-3]
        if stem == '__init__': stem = os.path.basename(os.path.dirname(f))
        cands = [t for t in tests if os.path.basename(t) in (f'test_{stem}.py', f'{stem}_test.py')] or [t for t in tests if stem in os.path.basename(t)]
        if cands: pick = sorted(cands, key=len)[0]; break
    if not pick: print('no matching test file found; run the issue example with `python - <<EOF` instead, then submit_patch')
    else:
        cmd = [sys.executable, '-m', 'pytest', pick, '-x', '-q', '-p', 'no:cacheprovider'] + (['-k', a.k] if a.k else [])
        rc, out = sh(cmd, root, a.timeout)
        print(f'test {pick}: {"PASS" if rc == 0 else "TIMEOUT" if rc == 124 else "FAIL rc=" + str(rc)}')
        if rc: print('\n'.join(out.strip().splitlines()[-15:])[-1500:])
    print(sh(['git', 'diff', '--stat'], root)[1].strip()[-600:])
    print('NEXT: if the failure is caused by your change, fix it once; otherwise call submit_patch now.')

if __name__ == '__main__':
    try: main()
    except Exception as e: print('check failed:', repr(e)[:200], '- call submit_patch if your edit is in place')
