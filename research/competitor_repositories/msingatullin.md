# B. msingatullin/gemma-4-developer-agent

- URL: https://github.com/msingatullin/gemma-4-developer-agent
- Inspected commit: `fe9ed0b` on `main` (2026-11-18). 292 commits from 2026-09-29 to 2026-11-18, most of them (146) on 2026-11-11 for the Paper Track. Other branches read: `fix/p0-honest-e4b-audit`, `agent/g0-portable-locator-20261112`, `main-track/v10-candidate`.
- License: Apache 2.0 (`LICENSE`, copied to `configs/msingatullin/LICENSE`).
- Size: 543 tracked files, 9.6 MB; ~470 of them under `paper/` (Paper Track study, not the agent).
- Verbatim copies in `configs/msingatullin/`: `v11_dev_31B_public_0.17/`, `v15_E4B_public_0.06/`, `v10_dev_unscored/`, `V15_V16_EXACT_DIFF.md`, `STATUS.md`, `HARNESS_README_as_republished.md`.

## Verdict in one line

The only repo in this set with a mid-table leaderboard score tied to a readable config: a **single 31B agent, no sub-agents, no LoRA, 28 tool calls, "edit by call 12"** reported at **public 0.17** (two submissions). Everything marketed in the README ("AST-guided verification", "traceback compression") is a Paper Track study on synthetic tasks and is **not** part of the scored agent.

## What is actually in the scored agent vs what is described

| Component | In README / paper | In the scored configs |
|---|---|---|
| AST symbol indexer / code slicing | Yes (paper, `submission/skills/ast_indexer`) | Not in v11 or v15. Early versions v1-v7 shipped SKILL.md files that are only prose with `python3 -c "import ast..."` one-liners. |
| Pre-flight `compile()` gate | Yes | v10: `python -m py_compile` after each edit. v11: only as a fallback "if no test can run". |
| Traceback compressor (B / B2) | Yes, Python code in `paper/traceback_compressor.py` | **Not in any agent.** The submission is declarative; a Python compressor cannot run in the harness. Closest thing is v10's `--tb=short --no-header` + `tail -25`. |
| AST+BM25 locator (v17) | `v17_small_model_candidate/skills/repo_locator/ast_locator.py` | Never submitted. STATUS.md: "integration unproven: issue text/query not supplied and tool path may not exist in /workspace". |
| Sub-agent `code_analyzer` / `bug_localizer` | v2-v10 | Dropped in v11. No score is recorded for v2-v10 anywhere in the repo. |

## Architecture of the scored configs

### v11 (31B, reported public 0.17) — `v11_dev/`

- `model: gemma-4-31b-it-qat-w4a16-ct`, single root agent, all 9 tools listed, **no sub-agents, no skills, no adapters**.
- Sampling: temp 0.2, top_p 0.95, `max_output_tokens` 8192, `thinking_budget` 4096, `include_thoughts: true`.
- `eval_config.yaml`: `timeout_seconds: 240`, `max_tool_calls: 28`, `max_time_minutes: 8`, `max_turns: 80`.
- Prompt (6.0 kB) is a call-indexed plan. Notable verbatim rules:
  - "28 tool calls and 8 minutes in total. When either runs out, the working tree is graded as it is. An edit that exists counts, even if you never call `submit_patch`. An unedited tree always scores zero."
  - "Calls 1-8: locate and read. Calls 9-12: edit. You MUST have edited a source file by call 12. If you are unsure, make your best-guess edit in the most likely place now. A wrong edit can still be corrected. Pure reading cannot score."
  - "Calls 13-20: verify and correct. Call 20 onward: no new exploration. Check, fix, submit."
  - "Never use `search_similar_code`, `get_code_neighbors` or `get_code_subgraph`. They return nothing useful."
  - "Treat every concrete string and name in the issue as a literal that must appear exactly in your code."
  - "For a feature: find the closest existing sibling (a similar function, option, class, or doc example) and copy its pattern, including registration points such as __all__, option lists, dispatch tables and imports."
  - Edit fallback: "After two matching failures, use one inline Python script through run_command with a quoted heredoc; assert that the old text occurs exactly once before replacing it and writing the file."
  - Verify "at most 2 calls": `timeout 150 python -m pytest tests/path/test_x.py -x -q -k keyword`; "Failures that come from missing fixtures, missing data, or import errors unrelated to your change are pre-existing. Ignore them."
  - "Call `submit_patch`. Confirm `patch_size > 0` and `files_changed > 0`. If either is 0, you have not edited anything. Edit now and submit again."
  - "Never conclude that nothing needs to change. Every task requires a non-empty source patch."
  - "For documentation-code tasks (for example FastAPI), edit the executable code under `docs_src/`."
- No reproduction-script phase at all. Search batching is encouraged ("combine independent searches ... into one run_command").

### v15 (E4B, reported public 0.06) and v16 (E4B, 0.05)

- v15: 6 tools (no graph tools), temp 0.2, top_k 64, thinking 4096, max_output 8192; budgets 6 min / 32 calls / 50 turns / 240 s.
- Same "edit by tool call 12" rule; "one check, one repair, then submit"; "If `get_status` shows less than 75 seconds remaining, call `submit_patch` immediately"; after submit "reply with the single plain-text word `Done.` and call no further tools. The harness only ends your session when you send a plain-text message without a tool call."
- v16 changed five things at once (temp 0.20 to 0.15, thinking 4096 to 2048, max_output 8192 to 4096, calls 32 to 36, reserve 75 s to 25 s, edit-by-12 rule relaxed) and scored 0.05. The author states the cause is "NOT ESTABLISHED"; one LB step is one task, so this is noise-level.

## Training

None. No LoRA, no adapters, no training script for the agent track.

## Verification approach

- In-agent (v11): narrow pytest on one file with `-k`, max 2 verify calls, then `git diff` self-audit against the issue's literal names and messages. No repro script.
- Offline tooling (CPU only, real): `tools/validate_submission.py`, real `adk_submission.compile_submission` on their zips (4/4 compile), RED/GREEN oracle checks for 8 pinned SWE-bench-style tasks using gold patches (not model patches), native `swegemma` tool smoke tests in Docker.
- No end-to-end local evaluation of the 31B agent on the dev set exists in the repo. The 31B agent was tuned purely against the leaderboard.

## Runtime

- v11: 8 min cap but 28 tool calls is the effective limiter. 8 min x ~120 tasks would exceed 12 h if every task hit the cap; the submission completed, so mean task time was well under the cap. No per-task timing is published.
- Their own static "benchmark" (`pilot/benchmark_v9_vs_v10_results.json`, branch `main-track/v10-candidate`) flagged v9 (no eval_config, harness default 60 min) as `GUARANTEED_TIMEOUT_EXCEEDS_12H`. That is a config lint, not a measurement.

## Evidence

| Claim | Value | Backing | Status |
|---|---|---|---|
| v11 31B public score | 0.17 | `STATUS.md` table with Kaggle submission id 57911135, "official Kaggle MCP get_competition_submission" | Author-reported with submission id. Not independently checkable by me. No archive hash for v11; that `v11_dev/` is byte-identical to the submitted zip is **unverified** (directory first committed 2026-11-06, commit `a1d4954`). |
| v14 31B public score | 0.17 | Submission id 58014403 | Author-reported. **v14 config is not in the repo**; what changed vs v11 is unknown. |
| v15 E4B public score | 0.06 | Submission id 58073369, zip SHA-256 `f8123775...`, unpacked files on branch `fix/p0-honest-e4b-audit` | Author-reported, best-documented artifact. |
| v16 E4B public score | 0.05 | Submission id 58126337, zip SHA-256 `b6c470a3...` | Author-reported. |
| Unquoted `*.py` glob bug: file HIT@5 1/9 to 4/9 by quoting | 9 pinned dev trees, raw stdout JSON on branch `agent/g0-portable-locator-20261112` (`docs/agent-g0/G0_SEARCH_006_*.json`) | Real CPU experiment with raw artifacts; model-free, manual query tokens, n=9. |
| E4B pilot: 3 prompt arms on pytest-11143 | 0/3 solved | `STATUS.md` 2026-11-13; custom JSON tool adapter, not the official harness | Real but n=1 and non-official harness. |
| "Paired E4B benchmark (+50% delta)" (commit `1c8bae2`) | 1/6 to 4/6 | **Retracted by the author**: `run_paired_e4b_eval.py` uses `simulate_v15_agent`/`simulate_v17_agent` with hardcoded patches (STATUS.md 2026-11-11/12) | Synthetic, retracted. |
| Traceback compression study | A raw 30/30, B compressor v1 25/30, B2 assertion-aware 29/30, C last-35-lines 30/30, D no traceback 22/30 | 150 archived model responses + patch execution JSONL under `paper/e2e_gemma_experiment/real_run_20261108/` | Real 31B inference, but 15 **synthetic single-shot** tasks, not agent runs; B2 is post-hoc. |
| Locator benchmark | Recall@1 47.6%, @5 64.3% on 42 tasks | `paper/small_model_benchmark/LOCATOR_BENCHMARK_RESULTS.json` | Localization only, zero solve-rate evidence (author's words). |
| Scores for v1-v10 (sub-agent era) | none recorded | Commits mention deploy refs 56695474 (v6) and 57779231 (v9) with no scores | Unknown. |

## Strengths

- A concrete, simple config associated with 0.17 on 31B.
- Unusually strict self-audit: simulated results were found and retracted in the open.
- The `*.py` quoting diagnosis is a real, reproducible, model-free finding.
- The traceback study gives a usable directional result about how much test output to keep.
- Republishes the harness guide (`docs/HARNESS_README.md`) with budget, compaction and patch-extraction details.

## Weaknesses

- No local dev-set evaluation of the scored agent; no per-task data; the two 0.17 scores cannot be decomposed.
- Enormous process overhead (hundreds of audit commits) with almost no agent-quality experiments after v11.
- README headline features are not in the scored agent.
- Scores rely on author statements; v14 is missing from the repo.

## Ideas worth adopting

1. **Call-indexed "edit by call N" deadline plus "an unedited tree always scores zero".** The only prompt structure in this set tied to 0.17, and it directly targets the failure mode measured independently in repo A (budget exhausted while exploring, diff=0) and repo C (60 calls, no patch). Our variant should express N relative to our own budget.
2. **Exploit the fallback extraction rule**: the working tree is graded even without `submit_patch`, so edit early and keep the tree in a submit-ready state at all times (no scratch files in `/workspace`, no test edits).
3. **Quote every pathspec/glob in prompt command templates** (`-- '*.py'`). Measured: unquoted `*.py` is expanded by bash when the repo root has any `.py` file, silently restricting `git grep` to root files; quoting alone moved gold-file HIT@5 from 1/9 to 4/9.
4. **Literal-spec extraction step with no tool call** ("every concrete string and name in the issue as a literal that must appear exactly") and the sibling-pattern rule for feature tasks (`__all__`, dispatch tables, sync/async twins). Hidden tests are written from the issue text.
5. **Do not compress failure output below the assertion.** Their real-inference study: no traceback 73%, lossy compressor 83%, raw or last-35-lines 100%. `tail -35`/`--tb=short` style truncation is safe; anything that drops the assertion line or `pytest.raises(match=...)` text is not.
6. **`edit_file` failure ladder**: re-read exact lines, never repeat an identical failed edit, then a heredoc Python replace that asserts exactly one occurrence.
7. **Post-submit check** `patch_size > 0` and `files_changed > 0`.

## Ideas to reject

1. **Banning the graph tools outright as a copied rule.** The claim "They return nothing useful" has no experiment behind it. Decide from our own traces (repo C independently notes the graph has sync "calls" edges only and misses async functions, so low value is plausible, but test it).
2. **Skill folders containing only prose.** They cost prompt/compile surface and there is no evidence the model loads them; the author removed them by v8.
3. **Shipping a Python locator or compressor as a skill script.** Unproven integration, never submitted, and the E4B pilot that tried locator prompts solved 0/3.
4. **Dropping verification to "at most 2 calls" as a fixed rule for 31B with a 5-minute budget** without measuring. It is defensible under a 28-call cap, but there is no evidence it is better than a repro-first loop; keep it as an A/B arm.
5. **Changing five knobs between submissions** (v15 to v16). One variable per daily submission, or decide locally.
6. **E4B as a main-track model**: 0.05-0.06 vs 0.17 for 31B with a near-identical prompt style.
