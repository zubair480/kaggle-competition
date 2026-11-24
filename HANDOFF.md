# Handoff: Gemma 4 Developer Agent competition

State on 2026-11-24 03:15 UTC. Read this first when continuing in a new session.

## Where things stand

- Competition: https://www.kaggle.com/competitions/gemma-4-developer-agent, Kaggle user `zubairzafar`.
  Final deadline 2026-12-02 23:59 UTC. One submission per day; none while another is scoring (about a day).
- Leaderboard results: `experiments/leaderboard/README.md`.
  - v3 (temperature 0.2, 5 min, 30 calls): **0.13** (8 of 58). Top of the board is 0.24.
  - v4 (v3 with temperature 1.0, top_k 64), submission 58739856: **0.12** (7 of 58).
- `submission/` holds v4. `experiments/v3_submitted/` is what scored 0.13.
  `experiments/v5_candidate/` is the next idea (plan-first prompt, tool-call fixes): validated, never run.
- Kaggle GPU quota (30 h a week) was used up on 2026-11-21. No local evaluation is possible until it resets.
- The owner declined using a hosted model service (OpenRouter) for local evaluation. Do not set it up unasked.
- The owner wants no submission made without their go-ahead after v4.

## What was learned (details in docs/ and research/)

- `docs/FINAL_REPORT.md`: all measured numbers. Our agent ties the public baseline locally (12 of 36).
- `docs/FAILURE_ANALYSIS.md`: a quarter of runs end with no edit; right file is found in 24 of 27 patched runs;
  only small fixes get solved.
- `docs/EVALUATION_INTEGRITY.md`: only 71 of 129 public tasks are usable (`data/sound_tasks.txt`).
- `research/competitor_repositories/idris_v24.md`: the published 0.24 bundle and what predicts success in
  its author's 1,104 runs (edit within two minutes; few searches; time past five minutes adds little).
- `research/small_model_methods_2026H2.md`: eight ranked experiments from recent papers (search extracts only).
- `research/competitor_repositories/kaggle_notebooks.md`: public notebooks; identical files swing 2-5 tasks.

## Open decision

v4 also landed low (0.12). Recommended next (candidate built in `experiments/v6_reference_idris_6min/`): submit the published 0.24 files (`research/competitor_repositories/idris_v24/v24/`)
with only the time cap shortened, as a reference point, before trying v5.

## How to do things

- Build / validate / smoke-test: `python scripts/build_submission.py`, `python scripts/validate_submission.py`,
  `python scripts/run_smoke_test.py --data <competition data dir>`. The last two need the harness wheels from
  Kaggle dataset `metric/gemma-4-developer-agent-wheelhouse` installed in a Python 3.12 or 3.13 venv.
- Submit / check score: `python3 scripts/submit_kaggle.py submit "description"` / `status`.
- GPU evaluation on Kaggle: `scripts/make_eval_notebook.py` then `scripts/kaggle_kernel.py push|status|output`;
  parse the log with `scripts/tools/parse_log.py`, classify with `scripts/classify_failures.py`.
- **Authentication:** in the cloud session the Kaggle token was injected by a network proxy, so these scripts
  call `curl` with no credentials. On another machine, add your Kaggle API token to the curl calls
  (for example `-u "$KAGGLE_USERNAME:$KAGGLE_KEY"`), or use the official `kaggle` command instead.
- Competition data is not in the repository (Kaggle rules); download it with the Kaggle API.

## Not in the repository

The cloud session's chat history, the downloaded competition data, the harness virtualenv and
`submission.zip` (rebuild it). A scheduled check for the v4 score lived in the cloud session only.
