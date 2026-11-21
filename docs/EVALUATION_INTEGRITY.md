# Evaluation integrity

All numbers here are measured with the official verifier (`swegemma 0.2.11`, Phase 2 `verify_task`, subprocess
sandbox) through `scripts/verify_patches.py`. Raw results are in `experiments/integrity/`.

## Summary

| Check | Kaggle official image (Python 3.12.13) | This container (Python 3.13) |
|---|---|---|
| Gold patch passes | **74 / 129** | 72 / 129 |
| Empty patch passes | **3 / 129** | 5 / 129 |
| Sound tasks (gold passes and empty fails) | **71 / 129** | not used |

**Only 71 of the 129 public tasks are a valid measuring stick in a Kaggle notebook.** The list is in
`data/sound_tasks.txt` (42 Rich, 29 FastAPI, 0 Requests, 0 HTTPX). Every local pass rate in this repository is
reported on sound tasks only.

## 6.1 Gold-patch checks

Run on Kaggle as a CPU notebook pinned to the same Docker image as the official starter notebook
(`gemma4-eval-integrity-gold-and-empty-patches`, 23.5 minutes).

- FastAPI: 31 of 67 gold patches pass. The failures exit with pytest code 2 (collection errors).
- Requests: 1 of 13 pass. Failures exit with code 1 (tests fail).
- Rich: 42 of 48 pass. One failure is a required test node that did not pass (`rich_3486`).
- HTTPX: 0 of 1.

In this container the same failures show their cause in the captured output: missing test dependencies
(`inline_snapshot` 24 tasks, `dirty_equals` 6, `typer` 1), collection errors, and 6 timeouts.

This reproduces what participants reported (thread 751487: 52/129 in a plain notebook, 127/129 after
rebuilding a scorer-like sandbox). Staff state that every hidden task passes with its gold patch
(threads 744951, 747248), so the breakage is a property of the public environment, not of the hidden scorer.

Not done: rebuilding the sandbox so all 129 pass. It would raise the usable public set from 71 to about 127,
but it means modifying the evaluation environment, and the remaining time was better spent on the agent.

## 6.2 Empty-patch checks

On the Kaggle image an empty patch is marked resolved for `fastapi_14851`, `fastapi_14077` and
`requests_6644`. In this container it is five tasks (`requests_7315`, `requests_7427`, `requests_7309`,
`fastapi_14851`, `fastapi_14077`).

These tasks cannot distinguish a working agent from a broken one and are excluded from the sound set. Nothing
in the agent tries to exploit this: the prompt always demands a real source change.

## 6.3 Dependency shadowing

Not directly measured. The evidence is indirect:

- The harness installs the checkout with `pip install -e /workspace --no-deps ... || true`, so a failed
  editable install is silent.
- Participants report that bundled release wheels can shadow `/workspace` (threads 751487, 745775), and repo C
  found its runtime importing an installed copy instead of the checkout.
- The Requests results fit that pattern: gold patches fail and some empty patches pass.

Consequence for the agent: a local test result inside the sandbox can be misleading. The prompt therefore
tells the agent to ignore failures that are unrelated or pre-existing, and not to chase missing packages.

## 6.4 Graph tools

- Wheelhouse: Kaggle dataset `metric/gemma-4-developer-agent-wheelhouse`, version 31, last updated
  2026-10-12. Package checksums were not recorded.
- Graph and embedding files exist for 127 of 129 public tasks.
- Similarity queries: 458 issued in `scripts/localization_benchmark.py`, 69 empty (15%), median latency 0.06 s.
- Coverage: a gold file is present in the graph for 109 of 129 tasks.
- Decision and full numbers: `docs/RETRIEVAL_RESEARCH.md`.

## What this means for our own measurements

1. A pass rate over all 129 tasks understates the agent: 58 tasks cannot pass regardless of the patch.
2. Requests and HTTPX give no signal at all in the public notebook environment.
3. The sound set is 71 tasks from two repositories, both of which the hidden set does not contain. Local
   results rank configurations only roughly; participants report local scores do not predict leaderboard
   order (threads 744319, 751973, 756400).
