"""Build a Kaggle notebook that evaluates submission/ on public tasks with the official harness
(same code path as the official starter notebook) and writes submission.zip.

usage: python scripts/make_eval_notebook.py OUT.ipynb [--ids-file ids.txt | --n 30] [--max-hours 3.0] [--submission-dir submission]
"""
import argparse, base64, io, json, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("--ids-file"); ap.add_argument("--n", type=int, default=0)
ap.add_argument("--max-hours", type=float, default=3.0); ap.add_argument("--submission-dir", default="submission")
a = ap.parse_args()

sub = ROOT / a.submission_dir
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(sub.rglob("*")):
        if p.is_file():
            z.write(p, p.relative_to(sub).as_posix())
blob = base64.b64encode(buf.getvalue()).decode()
ids = [l.strip() for l in Path(a.ids_file).read_text().splitlines() if l.strip()] if a.ids_file else []

nb = json.loads((ROOT / "experiments/notebooks/_starter_official.ipynb").read_text())
cells = nb["cells"]
def src(c): return "".join(c["source"])
def setsrc(c, s): c["source"] = s.splitlines(keepends=True); c["outputs"] = []; c["execution_count"] = None

overlay = f'''
# --- overlay: replace the sample agent with our submission (embedded zip) ---
import base64, io, zipfile, yaml
_BLOB = "{blob}"
if AGENT_DIR.exists():
    shutil.rmtree(AGENT_DIR)
AGENT_DIR.mkdir(parents=True)
zipfile.ZipFile(io.BytesIO(base64.b64decode(_BLOB))).extractall(AGENT_DIR)
MODEL_NAME = yaml.safe_load(open(AGENT_DIR / "agent.yaml").read().split("instruction:")[0])["model"]
print("agent files:", sorted(str(p.relative_to(AGENT_DIR)) for p in AGENT_DIR.rglob("*") if p.is_file()), "model:", MODEL_NAME)
'''
loop = f'''
import json as _json, time as _time
EVAL_IDS = {ids!r}
EVAL_N = {a.n}
MAX_HOURS = {a.max_hours}
if EVAL_IDS:
    _by = {{t.instance_id: t for t in tasks}}
    SAMPLE_TASKS = [_by[i] for i in EVAL_IDS if i in _by]
elif EVAL_N:
    SAMPLE_TASKS = tasks[:: max(1, len(tasks) // EVAL_N)][:EVAL_N]
else:
    SAMPLE_TASKS = []
limits, gen_constraints = build_submission_limits()
'''
record = '''
    _rec = dict(instance_id=task.instance_id, repo=task.repo, resolved=bool(result.resolved), exit_code=result.test_exit_code,
                patch_chars=len(patch), tool_calls=result.tool_calls, llm_calls=getattr(result, 'total_llm_calls', None),
                duration=round(result.duration_seconds, 1), wall=round(_time.time() - _t_task, 1), error=(result.error or '')[:300])
    with open(WORKING_DIR / 'task_results.jsonl', 'a') as _f:
        _f.write(_json.dumps(_rec) + '\\n')
    (WORKING_DIR / 'patches').mkdir(exist_ok=True)
    (WORKING_DIR / 'patches' / f'{task.instance_id}.patch').write_text(patch)
    try:  # compact per-task event digest in the notebook log (output files are not always retrievable)
        import re as _re
        _lg = (WORKING_DIR / 'results' / 'logs' / f'{task.instance_id}.log').read_text(errors='replace')
        _lg = _re.sub(r'\\x1b\\[[0-9;?]*[A-Za-z]', '', _lg)
        print('TRACE_BEGIN', task.instance_id)
        _keep = [_l for _l in _lg.splitlines() if _re.search(r'\\[\\s*[0-9.]+s\\]', _l[:16])]
        for _l in (_keep or _lg.splitlines())[:160]:
            if 'System Prompt' in _l or 'Task Prompt' in _l: continue
            print('T|', _l[:230])
        print('TRACE_END', task.instance_id)
        print('PATCH_BEGIN', task.instance_id); print(patch[:3000]); print('PATCH_END', task.instance_id)
    except Exception as _e:
        print('trace digest failed:', _e)
    if _time.time() - _t_run > MAX_HOURS * 3600:
        print('time budget for this dev run reached; stopping early'); break
'''
for c in cells:
    if c["cell_type"] != "code": continue
    s = src(c)
    if "SAMPLE_SUBMISSION_SRC = DATA_DIR / 'sample_submission'" in s:
        setsrc(c, s + overlay)
    elif "SAMPLE_TASKS = tasks[:2]" in s:
        s = s.replace("SAMPLE_TASKS = tasks[:2]\nlimits, gen_constraints = build_submission_limits()", loop)
        assert "EVAL_IDS" in s
        s = s.replace("for idx, task in enumerate(SAMPLE_TASKS, start=1):\n", "_t_run = _time.time()\nfor idx, task in enumerate(SAMPLE_TASKS, start=1):\n    _t_task = _time.time()\n")
        anchor = "        f'duration={result.duration_seconds:.1f}s'\n    )\n"
        assert anchor in s
        s = s.replace(anchor, anchor + record)
        s += "\nimport shutil as _sh\nif (WORKING_DIR / 'results').exists():\n    _sh.make_archive(str(WORKING_DIR / 'traces'), 'zip', root_dir=WORKING_DIR / 'results')\n    _sh.rmtree(WORKING_DIR / 'results', ignore_errors=True)\nserver_instance.stop()\n"
        setsrc(c, s)
    else:
        setsrc(c, s)
Path(a.out).write_text(json.dumps(nb))
print("wrote", a.out, "tasks:", len(ids) or a.n, "cells:", len(cells))
