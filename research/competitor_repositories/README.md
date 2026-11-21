# Competitor repositories — Gemma 4 Developer Agent Competition

Read-only analysis of public GitHub implementations, done 2026-11-21. No code from these repos was executed. Every score below is labelled by how it is backed; none could be checked against Kaggle directly from this sandbox.

Per-repo write-ups:

- [peoplerepabulic.md](peoplerepabulic.md) — A. Peoplerepabulic/kaggle-gemma4-developer-agent
- [msingatullin.md](msingatullin.md) — B. msingatullin/gemma-4-developer-agent
- [ns-0437.md](ns-0437.md) — C. ns-0437/gemma4-agent-lab
- [pluris.md](pluris.md) — D. github.com/pluris (attribution check; nothing found)
- [tfd-agent.md](tfd-agent.md) — E. rajrajak99/gemma4-tfd-agent (Kaggle discussion 745748)

Verbatim configs and prompts: [`configs/`](configs/) (each folder has `SOURCE_COMMIT.txt`; license files kept where the source had one).

## Comparison

| Implementation | Architecture | Training | Verification | Runtime | Evidence |
|---|---|---|---|---|---|
| **A. Peoplerepabulic** (commit `f063938`, 2026-11-03) | **12B**. Root (9 tools) + `code_analyzer` (read-only, 6 calls) + `patch_writer` (1 candidate, 4 calls). In-session best-of-3 with fixed strategies, ranked by repro, tests passed, diff size. | **Real LoRA SFT**: r16 / a32 / d0.05, q,k,v,o,gate,up,down, lr 1e-4 cosine, 3 epochs, max-len 8192, loss only on patch-producing assistant turns, chunked CE. Data: 14 gold rows (5 tasks) + 9 silver from 400 runs. **Adapter not adopted.** | `/tmp/repro.py` must fail first; narrowest test file; one-call CHECK_CANDIDATE (save diff, repro, tests, reset). Offline mirror `verifier_select.py`. | 4 min / 70 calls / 60 turns / 120 s. Measured ~4.6 s per tool call; mean sample time at the cap in every run. | Text log only (`docs/experiments.md`), no JSON. Starter 12B public **0.03** (asserted, indirectly linked). Local 12B: 2/30 and 16/100 tasks pass@4 (asserted). **Holdout A/B: base 2/29, gold LoRA 0/29, gold+silver LoRA 1/29** (asserted, cites Kaggle notebook version). Best-of-3 verifier: **unmeasured**. No LB score for the custom agent. |
| **B. msingatullin** (commit `fe9ed0b`, 2026-11-18) | **31B single agent**, no sub-agents, no skills, no LoRA (v11). Call-indexed plan: locate calls 1-8, **edit by call 12**, verify 13-20, submit. Graph tools forbidden in the prompt. E4B variant (v15) with 6 tools. Earlier v2-v10 used sub-agents and prose skills (no scores recorded). | None. | Max 2 verify calls: one named test file with `-k`; `git diff` audit against the issue's literal names; check `patch_size > 0`. No repro script. Paper-track traceback compressor and AST locator are **not** in the scored agent. | v11: 8 min / **28 calls** / 80 turns / 240 s. v15: 6 min / 32 calls / 50 turns. No timing data published. | Author-reported with Kaggle submission ids: **v11 31B 0.17** (57911135), v14 31B 0.17 (58014403, config not in repo), v15 E4B 0.06 (58073369, zip SHA recorded), v16 E4B 0.05. `v11_dev/` equals the submitted zip: unverified. Raw-artifact CPU study: quoting `'*.py'` moves gold-file HIT@5 1/9 to 4/9. Real 31B single-shot study on 15 synthetic tasks: raw traceback 30/30, lossy compression 25/30, no traceback 22/30. A "+50%" E4B benchmark was simulated and **retracted by the author**. |
| **C. ns-0437** (commit `3d3f417`, 2026-09-30) | **31B**. `swe_coder` (6 tools) + read-only `code_analyzer` (graph tools, ~12 calls). 600-1,250 word workflow prompt. `include_thoughts: false`. | None. | `py_compile`, repro, test file with preserved exit code, import-provenance check, test-path restore before submit. Heavy offline evidence tooling. | **No `eval_config.yaml`** (defaults). Pilot: 10 min / 100 calls / 60 turns. Measured 108 s / 23 calls thinking-off; 225 s / 44 calls and context overflow thinking-on (n=1 each). vLLM 31B ready in 6.3 min. | Owner-reported from a screenshot not in the repo: **v1, v2, v3 each 0.06** (v3 ref 56636116, zip SHA recorded; v3 source not in repo). **0 locally graded agent runs** (`docs/results.json`). |
| **D. pluris** | Unknown. | Unknown. | Unknown. | Unknown. | **No repo found.** GitHub API and profile page blocked; 15 guessed repo names do not resolve. Identity link to Kaggle "pluris" unproven. Nothing attributed. |
| **E. TFD-Agent** (commit `67a45cf`, 2026-09-30) | Custom non-ADK `agent.yaml` naming tools the harness does not have. 77-line dispatcher with **no model call**; demo runs a scripted fake repo. Targets 31B on paper. | Generic 4-bit QLoRA script (r16 / a32, lr 2e-4, 250 steps, max-seq 4096). No data, no adapter, no log. | Reproducer must fail then pass; innermost traceback frame fed back. Demo only. | `max_iterations: 30`, `timeout_seconds: 7200` (not harness keys). CSV runtimes 197-719 s are not from a real run. | README "45.6% Pass@1 SWE-bench Lite" has **no artifact**; values are hardcoded in a notebook cell. `benchmark_summary.csv` has 10 task titles repeated 5x and totals 47/50, contradicting the README. Dataset of "50 trajectories" not inspected. No attributable LB score. |

## Cross-repo findings that bear on engineering decisions

Ordered by strength of evidence.

1. **The simplest config has the highest reported score.** Single 31B agent, no sub-agents, no LoRA, 28 tool calls, forced early edit: 0.17 (B, author-reported). Coder + analyzer on 31B: 0.06 three times (C, owner-reported). 12B with sub-agents: 6-7% locally (A). Not a controlled comparison (budgets and prompts differ, and C shipped no `eval_config.yaml`), but there is no positive evidence for sub-agents anywhere in this set. Top public LB is 0.24, so B's v11 is the closest public reference point.
2. **The dominant measured failure mode is "no patch", not "wrong patch".** A: 40 calls spent exploring, diff=0. C: 60 turns, one probe repeated 56 times, zero patch; another run made 25 identical reads. B's prompt is built around this ("You MUST have edited a source file by call 12", "An unedited tree always scores zero"). The harness grades the working tree even without `submit_patch`.
3. **LoRA from self-collected trajectories did not help at small data scale.** A: 400 runs yielded 14 gold + 9 silver rows; on a 29-task holdout base 2/29, LoRA 0/29 and 1/29. Null/negative, inside noise, and the only LoRA measurement in the set. Nobody here has a positive LoRA result.
4. **Time per tool call is ~4.6-4.7 s on both 12B (A) and 31B thinking-off (C)** on L4x4. A 5-minute budget is therefore roughly 60 calls at most, fewer with long thinking or long outputs. A found time, not tool calls, binding at 4 min.
5. **Shell quoting in prompt command templates matters.** B: `git grep ... -- *.py` unquoted is glob-expanded by bash in repos with root-level `.py` files; quoting alone took gold-file HIT@5 from 1/9 to 4/9 (model-free, raw outputs archived).
6. **Keep the assertion text when truncating test output.** B's real-inference study (synthetic single-shot tasks): raw or last-35-lines 30/30, lossy compressor 25/30, assertion-aware compressor 29/30, no traceback 22/30.
7. **Harness traps reported independently by more than one repo**: scratch files must live in `/tmp` and be created by heredoc (`write_file` rejects `/tmp`; anything in `/workspace` enters the patch); test files and `conftest.py`/`pytest.ini` edits are stripped or harmful; `rg`/`tree` are absent; output is cut at 5,000 chars and `read_file` at 150 lines; `get_status` and `submit_patch` are free; `max_turns` exhaustion gives no warning; context compaction triggers at 14,336 tokens under a 32,768 window.
8. **Graph tools are distrusted by two authors without measurement** (B bans them; C says the graph only has synchronous "calls" edges and `search_similar_code` wants a symbol, not a sentence). Worth a quick local check before spending prompt space on them.
9. **Thinking settings are unresolved.** B's 0.17 config and A use `include_thoughts: true`, budget 4096; C uses `include_thoughts: false` and saw a context overflow in its one thinking-on run with a 100-call budget. No controlled result exists.

## What could not be verified

- Any Kaggle score: submission pages and leaderboard are not reachable from here. All scores are author statements; B and C cite submission ids, A cites a notebook version id.
- That B's `v11_dev/` is byte-identical to submission 57911135, and what B's v14 contained.
- C's v3 source (only its hash is in the repo) and the screenshot behind the 0.06 scores.
- A's raw `summary.json` files and adapters (not committed).
- The identity and any repository of "pluris".
- The contents of the TFD-Agent Kaggle dataset and notebook.
