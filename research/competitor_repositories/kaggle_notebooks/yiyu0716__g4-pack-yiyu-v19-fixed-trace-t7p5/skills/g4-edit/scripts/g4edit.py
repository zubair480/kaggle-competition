#!/usr/bin/env python3
"""Apply SEARCH/REPLACE blocks read from stdin to one repository file.

    python3 /tmp/g4edit.py --check   # before submit_patch: cleanup, closest tests, diff
    python3 /tmp/g4edit.py --trace /tmp/repro.py   # repository functions a reproduction runs

    python3 /tmp/g4edit.py path/to/file.py <<'EDIT'
    <<<<<<< SEARCH
    exact current lines
    =======
    replacement lines
    >>>>>>> REPLACE
    EDIT

Every block must match the current file exactly once (trailing whitespace and
indentation are tolerated, then re-indented). Python results must compile. The
file is replaced atomically only if every block applies; otherwise it is left
unchanged and the reason is printed. Exit codes: 0 applied, 1 not applied,
2 usage error.
"""
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

SEARCH = re.compile(r'^\s*<{5,9} ?SEARCH\s*$')
DIVIDER = re.compile(r'^\s*=======\s*$')
REPLACE = re.compile(r'^\s*>{5,9} ?REPLACE\s*$')
USAGE = ("usage: python3 /tmp/g4edit.py path/to/file.py <<'EDIT'\n"
         "<<<<<<< SEARCH\nexact current lines\n=======\nreplacement lines\n>>>>>>> REPLACE\nEDIT")
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.g4edit_state.json')


class NotApplied(Exception):
    def __init__(self, message, context=''):
        super().__init__(message)
        self.context = context  # current code around the target, shown when the command repeats


def region(lines, start, length, margin=12, limit=3500):
    lo, hi = max(0, start - margin), min(len(lines), start + max(length, 1) + margin)
    shown, size = [], 0
    for j in range(lo, hi):
        row = '%5d| %s' % (j + 1, lines[j][:200])
        if size + len(row) > limit:
            break
        shown.append(row)
        size += len(row) + 1
    return 'Current %s lines %d-%d:\n%s' % ('code', lo + 1, lo + len(shown), '\n'.join(shown))


def protected(rel):
    parts = rel.lower().split('/')
    name = parts[-1]
    return ('.git' in parts
            or any(part in ('test', 'tests') for part in parts[:-1])
            or name in ('conftest.py', 'pytest.ini')
            or (name.endswith('.py') and (name.startswith('test_') or name.endswith('_test.py'))))


def toplevel():
    try:
        out = subprocess.run(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, check=True)
        return os.path.realpath(out.stdout.decode().strip())
    except Exception:
        return os.path.realpath(os.getcwd())


def untranslate(text, root):
    # The subprocess sandbox rewrites literal /tmp and /workspace in commands to
    # its own directories; undo that inside the edit text.
    tmp = os.environ.get('TMPDIR')
    if tmp and os.path.basename(root) == 'workspace':
        base = os.path.dirname(root)
        if os.path.realpath(os.path.dirname(tmp)) == base and os.path.basename(tmp.rstrip('/')) == 'tmp':
            text = text.replace(base + '/workspace', '/workspace').replace(base + '/tmp', '/tmp')
    return text


def parse(text):
    blocks, lines, i = [], text.replace('\r\n', '\n').split('\n'), 0
    while i < len(lines):
        if not SEARCH.match(lines[i]):
            i += 1  # text outside blocks (a file name, a fence) is ignored
            continue
        j = i + 1
        while j < len(lines) and not DIVIDER.match(lines[j]):
            if SEARCH.match(lines[j]) or REPLACE.match(lines[j]):
                raise NotApplied('USAGE: block %d has no ======= line\n%s' % (len(blocks) + 1, USAGE))
            j += 1
        k = j + 1
        while k < len(lines) and not REPLACE.match(lines[k]):
            if SEARCH.match(lines[k]) or DIVIDER.match(lines[k]):
                break
            k += 1
        if j >= len(lines) or k >= len(lines) or not REPLACE.match(lines[k]):
            raise NotApplied('USAGE: block %d is not closed by >>>>>>> REPLACE\n%s' % (len(blocks) + 1, USAGE))
        blocks.append((lines[i + 1:j], lines[j + 1:k]))
        i = k + 1
    if not blocks:
        raise NotApplied('USAGE: no SEARCH/REPLACE block on stdin\n' + USAGE)
    return blocks


def windows(file_lines, search, key):
    n, target = len(search), [key(x) for x in search]
    keys = [key(x) for x in file_lines]
    return [i for i in range(len(file_lines) - n + 1) if keys[i:i + n] == target]


def indent(line):
    return line[:len(line) - len(line.lstrip())]


def reindent(replace, search, window):
    src = next((indent(x) for x in search if x.strip()), '')
    dst = next((indent(x) for x in window if x.strip()), '')
    if src == dst:
        return replace
    if dst.startswith(src):
        extra = dst[len(src):]
        return [extra + x if x.strip() else x for x in replace]
    if src.startswith(dst):
        cut = len(src) - len(dst)
        return [x[cut:] if x[:cut].strip() == '' else x.lstrip() for x in replace]
    return replace


def closest(file_lines, search):
    n = max(1, len(search))
    want = '\n'.join(x.strip() for x in search)
    best, where = 0.0, 0
    for i in range(0, max(1, len(file_lines) - n + 1)):
        got = '\n'.join(x.strip() for x in file_lines[i:i + n])
        matcher = difflib.SequenceMatcher(None, want, got, autojunk=False)
        if matcher.real_quick_ratio() > best and matcher.quick_ratio() > best:
            ratio = matcher.ratio()
            if ratio > best:
                best, where = ratio, i
    lo, hi = max(0, where - 1), min(len(file_lines), where + n + 1)
    return '\n'.join('%5d| %s' % (j + 1, file_lines[j][:160]) for j in range(lo, min(hi, lo + 12))), where


def numbered(lines, start, mark=None):
    return '\n'.join('%s%5d| %s' % ('>' if j == mark else ' ', j + 1, lines[j][:160])
                     for j in range(max(0, start), min(len(lines), start + 7)))


def apply_block(lines, search, replace, number):
    if not search:
        raise NotApplied('block %d has an empty SEARCH section, but the file already has content; '
                         'copy the lines to change (or the lines around an insertion) into SEARCH' % number)
    if (replace and len(replace) > len(search) and windows(replace, search, lambda x: x.rstrip())
            and len(windows(lines, replace, lambda x: x.rstrip())) == 1):
        at = windows(lines, replace, lambda x: x.rstrip())[0]
        return lines, 'already present', region(lines, at, len(replace), 4)  # an insertion already made
    for name, key in (('exact', lambda x: x), ('trailing whitespace', lambda x: x.rstrip())):
        found = windows(lines, search, key)
        if len(found) == 1:
            i = found[0]
            new = lines[:i] + replace + lines[i + len(search):]
            return new, name, region(new, i, len(replace), 4)
        if len(found) > 1:
            raise NotApplied('block %d: SEARCH matches %d places (lines %s); add surrounding lines so it '
                             'matches exactly once' % (number, len(found), ', '.join(str(i + 1) for i in found[:8])),
                             region(lines, found[0], len(search), 6))
    if len(search) == 1 and len(replace) == 1 and search[0].strip():
        fragment = re.compile(r'(?<!\w)' + re.escape(search[0].strip()) + r'(?!\w)')
        hits = [(i, m) for i, line in enumerate(lines) for m in fragment.finditer(line)]
        if len(hits) == 1:
            (i, m), new = hits[0], replace[0].strip()
            changed = lines[:i] + [lines[i][:m.start()] + new + lines[i][m.end():]] + lines[i + 1:]
            return changed, 'fragment', region(changed, i, 1, 4)
    found = windows(lines, search, lambda x: x.strip())
    if len(found) == 1:
        i = found[0]
        new = lines[:i] + reindent(replace, search, lines[i:i + len(search)]) + lines[i + len(search):]
        return new, 'indentation', region(new, i, len(replace), 4)
    if len(found) > 1:
        raise NotApplied('block %d: SEARCH matches %d places when indentation is ignored (lines %s); add '
                         'surrounding lines' % (number, len(found), ', '.join(str(i + 1) for i in found[:8])),
                         region(lines, found[0], len(search), 6))
    significant = [x.strip() for x in replace if x.strip()]
    if (len(significant) >= 2 or (significant and len(significant[0]) >= 16)) and \
            len(windows(lines, replace, lambda x: x.rstrip())) == 1:
        at = windows(lines, replace, lambda x: x.rstrip())[0]
        return lines, 'already present', region(lines, at, len(replace), 4)
    present = windows(lines, replace, lambda x: x.rstrip()) if significant else []
    hint = ('\nThe REPLACE text already appears at line %d; if that is your earlier edit, it is already '
            'applied.' % (present[0] + 1)) if len(present) == 1 else ''
    near, where = closest(lines, search)
    raise NotApplied('block %d: SEARCH text not found. Closest current lines (copy SEARCH from these, '
                     'without the line numbers):\n%s%s' % (number, near, hint), region(lines, where, len(search)))


SCRATCH = re.compile(r'^(repro|reproduce|reproduction|debug|scratch|tmp|temp|check|verify|test)[\w.-]*'
                     r'\.(py|txt|sh|json|log|out)$|^[\w.-]*_test\.py$', re.I)


def git(*args):
    return subprocess.run(['git', *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


GENERIC = {'__init__', 'utils', 'util', 'main', 'base', 'core', 'compat', '_compat', 'types', 'typing',
           'models', 'helpers', 'common', 'constants', 'exceptions', 'errors'}


def baseline_ref():
    return '_swegemma_baseline' if git('rev-parse', '--verify', '-q', '_swegemma_baseline^0').returncode == 0 else 'HEAD'


def cleanup(base):
    changed = git('diff', '--name-only', '--no-renames', '-z', base, '--')
    untracked = git('ls-files', '--others', '--exclude-standard', '-z')
    if changed.returncode or untracked.returncode:
        raise RuntimeError((changed.stderr or untracked.stderr).decode()[:300])
    tracked = [p for p in changed.stdout.decode('utf-8', 'replace').split('\0') if p]
    new = [p for p in untracked.stdout.decode('utf-8', 'replace').split('\0') if p]
    restored, removed = [], []
    for path in tracked:
        if protected(path):
            exists = git('cat-file', '-e', '%s:%s' % (base, path)).returncode == 0
            result = git('checkout', base, '--', path) if exists else git('rm', '-q', '-f', '--cached', '--', path)
            if not exists and os.path.lexists(path):
                os.unlink(path)
            (restored if result.returncode == 0 else removed).append(path)
    for path in new:
        if protected(path) or ('/' not in path and SCRATCH.match(path)) or os.path.basename(path).startswith('.g4edit-'):
            if os.path.isfile(path) or os.path.islink(path):
                os.unlink(path)
                removed.append(path)
    return restored, removed, new


def changed_files(base):
    left = git('diff', '--name-only', '--no-renames', '-z', base, '--').stdout.decode('utf-8', 'replace').split('\0')
    new = git('ls-files', '--others', '--exclude-standard', '-z').stdout.decode('utf-8', 'replace').split('\0')
    return sorted({p for p in left + new if p}), {p for p in new if p}


def related_tests(sources, limit=6):
    listed = git('ls-files', '-z').stdout.decode('utf-8', 'replace').split('\0')
    tests = [p for p in listed if p.endswith('.py') and protected(p) and os.path.basename(p).startswith('test')]
    scores, texts = {}, {}
    for source in sources:
        parts = source[:-3].split('/')
        if parts and parts[0] == 'src':
            parts = parts[1:]
        if parts and parts[-1] == '__init__':
            parts = parts[:-1]
        if not parts:
            continue
        dotted, stem = '.'.join(parts), parts[-1].lstrip('_')
        parent = parts[-2].lstrip('_') if len(parts) > 1 else ''
        for test in tests:
            name = os.path.basename(test)[:-3]
            score = 0
            if stem and stem not in GENERIC and stem in name:
                score += 3
            if parent and parent not in GENERIC and parent[:8] in name:
                score += 1
            if test not in texts:
                try:
                    with open(test, encoding='utf-8', errors='replace') as handle:
                        texts[test] = handle.read()
                except OSError:
                    texts[test] = ''
            text = texts[test]
            if 'import ' + dotted in text or 'from ' + dotted + ' import' in text or (
                    len(parts) > 1 and 'from %s import %s' % ('.'.join(parts[:-1]), parts[-1]) in text):
                score += 4
            if score:
                scores[test] = scores.get(test, 0) + score
    return sorted(scores, key=lambda test: (-scores[test], test))[:limit]


def check():
    """Clean test/scratch files, name the closest existing tests and show the diff (no automatic verdict)."""
    root = toplevel()
    os.chdir(root)
    base = baseline_ref()
    try:
        restored, removed, new = cleanup(base)
    except RuntimeError as error:
        return 'CHECK_FAILED: git could not list changes: %s' % error, 1
    left, untracked = changed_files(base)
    sources = [p for p in left if p.endswith('.py') and not protected(p) and os.path.isfile(p)]
    lines = ['CHECK_DONE: restored %d test file(s)%s; removed %d test/scratch file(s)%s.' % (
        len(restored), (': ' + ', '.join(restored[:10])) if restored else '',
        len(removed), (': ' + ', '.join(removed[:10])) if removed else '')]
    lines.append('Files your patch now changes: %s' % (', '.join(left[:30]) if left else 'NONE (empty patch)'))
    if any(not protected(p) and '/' not in p and p.endswith('.py') and p in untracked for p in left):
        lines.append('Check that new files at the repository root are really part of the fix.')
    tests = related_tests(sources) if sources else []
    if tests:
        lines.append('Closest existing tests for the changed modules: %s' % ', '.join(tests))
        lines.append('Run them (python -m pytest FILE -q). A failure is expected only where a test asserts the old '
                     'behaviour the issue asks to change; any other failure means the change broke something.')
    diff = git('diff', '--no-color', '-U2', base, '--').stdout.decode('utf-8', 'replace')
    if diff:
        lines.append(diff[:2500] + ('\n... (diff truncated)' if len(diff) > 2500 else ''))
    lines.append('Submit only when the diff above is the complete source fix for the issue.' if left
                 else 'Make the source fix before submitting.')
    return '\n'.join(lines), 0


TRACE_USAGE = ('USAGE: python3 /tmp/g4edit.py --trace /tmp/repro.py [args]  or  '
               'python3 /tmp/g4edit.py --trace -c "python code"')


def trace(argv):
    """Run a reproduction in-process and list the repository functions it executes."""
    import io
    import runpy
    import threading
    import traceback
    root = toplevel()
    if not argv or (argv[0] == '-c' and len(argv) < 2):
        return TRACE_USAGE, 2
    code = argv[1] if argv[0] == '-c' else None
    script = None if code is not None else os.path.realpath(argv[0])
    if script and not os.path.isfile(script):
        return 'TRACE: %s does not exist. %s' % (argv[0], TRACE_USAGE), 2
    cache, calls, order = {}, {}, []

    def relative(filename):
        result = cache.get(filename)
        if result is None:
            real = os.path.realpath(filename) if filename and not filename.startswith('<') else ''
            result = os.path.relpath(real, root) if real.startswith(root + os.sep) and real != script else ''
            if result and (protected(result) or result.startswith('.')):
                result = ''
            cache[filename] = result
        return result

    def profile(frame, event, arg):
        # CO_OPTIMIZED (0x1) marks real functions; class bodies and module code are import noise.
        if event == 'call' and frame.f_code.co_flags & 0x1 and not frame.f_code.co_name.startswith('<'):
            rel = relative(frame.f_code.co_filename)
            if rel:
                key = (rel, frame.f_code.co_name, frame.f_code.co_firstlineno)
                if key in calls:
                    calls[key] += 1
                else:
                    calls[key] = 1
                    order.append(key)

    out, saved = io.StringIO(), (sys.stdout, sys.stderr, list(sys.argv), list(sys.path))
    status, path = 'finished without an exception', []
    sys.argv = ['-c'] + argv[2:] if code is not None else list(argv)
    sys.path[0] = '' if code is not None else os.path.dirname(script)
    sys.stdout = sys.stderr = out
    threading.setprofile(profile)
    sys.setprofile(profile)
    try:
        if code is not None:
            exec(compile(code, '<string>', 'exec'), {'__name__': '__main__'})
        else:
            runpy.run_path(script, run_name='__main__')
    except SystemExit as error:
        status = 'exited with code %s' % (error.code,)
    except BaseException as error:  # the reproduction's own failure is the point of tracing
        status = 'raised %s: %s' % (type(error).__name__, str(error)[:200])
        path = [(relative(f.filename), f.lineno, f.name) for f in traceback.extract_tb(error.__traceback__)]
        path = [p for p in path if p[0]]
    finally:
        sys.setprofile(None)
        threading.setprofile(None)
        sys.stdout, sys.stderr, sys.argv[:], sys.path[:] = saved[0], saved[1], saved[2], saved[3]
    lines = ['TRACE: %s %s.' % ('-c code' if code is not None else argv[0], status)]
    if path:
        lines.append('Exception path in the repository (innermost last):')
        lines += ['  %s:%d in %s' % p for p in path[-8:]]
    if not order:
        lines.append('No repository function was executed (is the package imported from /workspace?).')
    else:
        files = []
        for key in order:
            if key[0] not in files:
                files.append(key[0])
        lines.append('Repository functions executed, by file in first-call order (name@line xcalls):')
        size = sum(len(line) for line in lines)
        for index, name in enumerate(files):
            funcs = [k for k in order if k[0] == name]
            shown = ', '.join('%s@%d%s' % (k[1], k[2], ' x%d' % calls[k] if calls[k] > 1 else '') for k in funcs[:10])
            row = '  %s (%d): %s%s' % (name, len(funcs), shown, ', ...' if len(funcs) > 10 else '')
            if size + len(row) > 3300:
                lines.append('  ... %d more file(s): %s' % (len(files) - index, ', '.join(files[index:index + 12])))
                break
            lines.append(row)
            size += len(row)
        lines.append('The fix is normally in one of these functions; read the most specific ones before editing.')
    printed = out.getvalue()
    if printed:
        lines.append('--- reproduction output (last 600 characters) ---')
        lines.append(printed[-600:])
    return '\n'.join(lines), 0


def remember(key):
    try:
        state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    except Exception:
        state = {}
    count = state.get(key, 0) + 1
    state[key] = count
    try:
        with open(STATE, 'w') as out:
            json.dump(state, out)
    except Exception:
        pass
    return count


def run(argv, stdin):
    if len(argv) != 1 or argv[0].startswith('-'):
        raise NotApplied('USAGE: give exactly one file path\n' + USAGE)
    root = toplevel()
    path = os.path.realpath(os.path.join(os.getcwd(), argv[0]))
    if path != root and not path.startswith(root + os.sep):
        raise NotApplied('%s is outside the repository %s' % (argv[0], root))
    rel = os.path.relpath(path, root)
    if protected(rel):
        raise NotApplied('PROTECTED: %s is a test/configuration path; fix the source instead and check '
                         'behaviour with a script in /tmp' % rel)
    blocks = parse(untranslate(stdin, root))
    exists = os.path.exists(path)
    if exists and not os.path.isfile(path):
        raise NotApplied('%s is not a regular file' % rel)
    raw = open(path, 'rb').read() if exists else b''
    bom = raw.startswith(b'\xef\xbb\xbf')
    try:
        text = raw[3:].decode('utf-8') if bom else raw.decode('utf-8')
    except UnicodeDecodeError:
        raise NotApplied('%s is not UTF-8 text' % rel)
    newline = '\r\n' if '\r\n' in text else '\n'
    final_newline = text.endswith(newline) or not text
    lines = text.split(newline)
    if final_newline:
        lines.pop()
    notes, contexts = [], []
    if not text:
        if len(blocks) != 1 or blocks[0][0]:
            raise NotApplied('%s does not exist or is empty: use one block with an empty SEARCH section to '
                             'create it' % rel)
        lines, notes = list(blocks[0][1]), ['new file' if not exists else 'filled empty file']
    else:
        for number, (search, replace) in enumerate(blocks, 1):
            lines, how, context = apply_block(lines, search, replace, number)
            notes.append(how)
            contexts.append(context)
    new_text = newline.join(lines) + (newline if final_newline and lines else '')
    if exists and new_text == text:
        return ('ALREADY_APPLIED %s: SEARCH is gone and the REPLACE text is already in the file; file '
                'unchanged. Do not resend this edit; run your reproduction or tests next.\n%s'
                % (rel, contexts[-1] if contexts else '')), 0
    if path.endswith('.py'):
        try:
            compile(text, path, 'exec', dont_inherit=True)
            original_compiles = True
        except (SyntaxError, ValueError):
            original_compiles = False
        if original_compiles:
            try:
                compile(new_text, path, 'exec', dont_inherit=True)
            except SyntaxError as error:
                where = (error.lineno or 1) - 1
                raise NotApplied('SYNTAX_ERROR: the edited %s would not compile: %s (line %s). Fix the '
                                 'REPLACE text (indentation, brackets, quotes):\n%s' % (
                                     rel, error.msg, error.lineno, numbered(new_text.split(newline), where - 3, where)),
                                 region(text.split(newline), max(0, where - 3), 6))
    directory = os.path.dirname(path)
    if not exists:
        os.makedirs(directory, exist_ok=True)
    mode = os.stat(path).st_mode & 0o7777 if exists else 0o644
    fd, temporary = tempfile.mkstemp(prefix='.g4edit-', dir=directory)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write((b'\xef\xbb\xbf' if bom else b'') + new_text.encode('utf-8'))
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise
    diff = list(difflib.unified_diff(text.split(newline), new_text.split(newline), 'a/' + rel, 'b/' + rel,
                                     lineterm='', n=1))
    shown = '\n'.join(x[:160] for x in diff[:40]) + ('\n... (%d more diff lines)' % (len(diff) - 40) if len(diff) > 40 else '')
    return 'APPLIED %s (%d block%s: %s)\n%s' % (rel, len(blocks), '' if len(blocks) == 1 else 's',
                                               ', '.join(notes), shown), 0


def main():
    if sys.argv[1:] == ['--check']:
        message, code = check()
        print(message)
        return code
    if sys.argv[1:2] == ['--trace']:
        message, code = trace(sys.argv[2:])
        print(message)
        return code
    stdin = '' if sys.stdin is None or sys.stdin.isatty() else sys.stdin.read()
    key = hashlib.sha256(('\0'.join([os.getcwd()] + sys.argv[1:] + [stdin])).encode('utf-8', 'replace')).hexdigest()[:20]
    count = remember(key)
    try:
        message, code = run(sys.argv[1:], stdin)
        if count > 1 and message.startswith('ALREADY_APPLIED'):
            message += ('\nThis identical command has now been sent %d times and is already applied. Do not send '
                        'it again.' % count)
    except NotApplied as error:
        message = str(error)
        code = 2 if message.startswith('USAGE') else 1
        message = 'NOT_APPLIED (file unchanged): ' + message
        if count > 1:
            message += ('\nThis identical command has now failed %d times. Do not resend it: build a different '
                        'SEARCH from the current code below.' % count)
            if error.context:
                message += '\n' + error.context
    print(message)
    return code


if __name__ == '__main__':
    sys.exit(main())
