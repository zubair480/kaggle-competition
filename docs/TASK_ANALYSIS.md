# Public task analysis (129 tasks)

Produced by `scripts/analyze_tasks.py` from `tasks.jsonl`. Per-task rows are in `data/task_analysis.csv`,
aggregates in `data/task_taxonomy.json`, validation splits in `data/splits.json`.

Reference patches and test patches were read here for offline statistics only. Nothing derived from them is
in `submission/`.

## Composition

| Repository | Tasks | Median changed lines | Easy / medium / hard (heuristic) |
|---|---|---|---|
| fastapi/fastapi | 67 | 18 | 31 / 19 / 17 |
| Textualize/rich | 48 | 9 | 26 / 17 / 5 |
| psf/requests | 13 | 4 | 11 / 2 / 0 |
| encode/httpx | 1 | 79 | 0 / 0 / 1 |

Tasks were created between 2023-07-29 and 2026-06-20. No task has hints (`hints_text` is always empty).

## What a reference fix looks like

- **Small and local.** 71% of fixes touch one file. The median fix changes 12 lines; the 75th percentile is 44,
  the 90th is 128. Seven tasks change more than 300 lines (one changes 12,714) and are out of reach for a
  5-minute agent.
- **Usually a bug fix.** By title: 57 bug fixes, 31 features, 4 maintenance, 37 unclassified.
- **Sometimes a new file.** 11 tasks (8.5%) create a file; the tests then import exact names from it.
- **Multi-file source changes** occur in 37 tasks (29%); 18% span more than one directory.
- **Four tasks change no library source at all** (scripts, docs examples). `fastapi_15661`, for example, adds
  `scripts/prepare_release.py`.

## What the issue text gives the agent

- **Short.** Median 418 characters; 90th percentile 1,891.
- **Rarely names the file.** The gold file name appears in 8% of issues. A changed function or class name
  appears in 23%. The agent has to search by behaviour and identifiers, not by path.
- **A quarter are pull-request descriptions**, not bug reports (25%), mostly in FastAPI. They describe the change
  that was made, so the wording maps directly onto the required edit.

## Keyword taxonomy (a task can be in several)

http behaviour 46, typing/annotations 42, terminal rendering 36, tooling/CI 34, compatibility/deprecation 32,
validation/errors 25, docs examples 24, serialization/encoding 19, async 16, dependency injection 13,
OpenAPI schema 12, performance 11.

## Difficulty heuristic

Easy = at most 15 changed lines in one file (68 tasks). Medium = at most 80 lines in at most 3 files (38).
Hard = the rest (23). This is derived from the reference patch size, not from measured agent success.

## Consequences for the agent

1. The realistic target is the 68 easy plus part of the 38 medium tasks. The prompt should push for a small,
   early edit and not spend calls on broad exploration.
2. Because the file is almost never named, the first step must be an identifier search. See
   `docs/RETRIEVAL_RESEARCH.md` for which search works.
3. For features, exact public names matter: hidden tests import them.
4. Public-set results will overstate hidden-set results. Community runs resolve 35-43% of these tasks while the
   best public leaderboard score is 24%.

## Splits

- Task level: 99 dev / 30 holdout, assigned by hash of the task id.
- Repository level: tune on FastAPI + Requests and check on Rich, and the reverse, to estimate transfer to
  repositories the agent was not tuned on.
