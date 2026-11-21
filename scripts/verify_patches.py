"""Run the official swegemma Phase-2 verifier on supplied patches (no model needed).

modes:  gold   -> apply each task's reference patch (evaluator sanity check)
        empty  -> apply no patch (tests must FAIL, otherwise the task is unreliable)
        file   -> apply patches from a directory of <instance_id>.patch files

usage: python scripts/verify_patches.py --data DATA_DIR --mode gold --out results.jsonl [--ids a b] [--jobs 3]
Reference patches are used for offline evaluator validation only; they never enter the submission.
"""
import argparse, asyncio, json, sys, time
from pathlib import Path

from adk_eval_core import SessionTrace  # type: ignore
from swegemma.config import EvalConfig
from swegemma.evaluate import Evaluator
from swegemma.models import load_tasks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--mode", choices=["gold", "empty", "file"], required=True)
    ap.add_argument("--patch-dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--work", default="/tmp/verify_results")
    a = ap.parse_args()
    data = Path(a.data)
    tasks = load_tasks(data / "tasks.jsonl")
    if a.ids:
        tasks = [t for t in tasks if t.instance_id in set(a.ids)]
    done = set()
    out = Path(a.out)
    if out.exists():
        done = {json.loads(l)["instance_id"] for l in out.read_text().splitlines() if l.strip()}
    tasks = [t for t in tasks if t.instance_id not in done]

    def patch_for(task):
        if a.mode == "gold":
            return task.patch
        if a.mode == "empty":
            return ""
        p = Path(a.patch_dir) / f"{task.instance_id}.patch"
        return p.read_text() if p.exists() else ""

    class Replay(Evaluator):
        async def _run_agent_sandbox(self, task, *args, **kw):
            return patch_for(task), None, SessionTrace()

    cfg = EvalConfig(
        tasks_path=data / "tasks.jsonl", snapshots_dir=data / "snapshots", results_dir=Path(a.work),
        submission_dir=None, models=None, sandbox="subprocess", wheels_dir=data / "wheels",
        graph_dir=str(data / "graphs"), embeddings_dir=str(data / "embeddings"),
        verification_timeout_seconds=300, skip_agent_patch=(a.mode == "empty"), display_mode="quiet",
    )
    ev = Replay(cfg)
    sem = asyncio.Semaphore(a.jobs)

    async def one(i, task):
        async with sem:
            t0 = time.time()
            try:
                r = await ev.evaluate_task(task=task, task_index=i, total_tasks=len(tasks))
                rec = dict(instance_id=task.instance_id, repo=task.repo, mode=a.mode, resolved=bool(r.resolved),
                           exit_code=r.test_exit_code, error=(r.error or "")[:500],
                           tail=(r.test_output or "")[-600:], seconds=round(time.time() - t0, 1))
            except Exception as e:  # keep going; record the failure
                rec = dict(instance_id=task.instance_id, repo=task.repo, mode=a.mode, resolved=False,
                           exit_code=-99, error=f"{type(e).__name__}: {e}"[:500], tail="", seconds=round(time.time() - t0, 1))
            with out.open("a") as f:
                f.write(json.dumps(rec) + "\n")
            print(rec["instance_id"], rec["resolved"], rec["exit_code"], rec["seconds"], rec["error"][:120], flush=True)

    async def run():
        await asyncio.gather(*(one(i, t) for i, t in enumerate(tasks, 1)))

    asyncio.run(run())


if __name__ == "__main__":
    main()
