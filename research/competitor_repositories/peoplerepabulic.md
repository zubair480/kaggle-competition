# A. Peoplerepabulic/kaggle-gemma4-developer-agent

- URL: https://github.com/Peoplerepabulic/kaggle-gemma4-developer-agent
- Inspected commit: `f063938` (2026-11-03). 25 commits, 2026-10-22 to 2026-11-03, single author (Kaggle account `cheeway`).
- License: none in repo (no LICENSE file). Treat copied text as reference only.
- Size: 31 tracked files. No adapters, no result JSON, no trace files committed. All numbers live in `docs/experiments.md`.
- Verbatim copies: `configs/peoplerepabulic/` (whole `agent/` tree + `experiments.md`).

## Verdict in one line

The most honest negative-result log of the set: 12B base model, measured local pass rates of 6-7% task-level, a LoRA A/B on a 29-task holdout that did **not** help (base 2/29, gold-LoRA 0/29, gold+silver-LoRA 1/29), and an in-session best-of-3 verifier that is implemented in the prompt but **never measured**.

## Architecture (implemented, in `agent/`)

- Model: `gemma-4-12b-it-qat-w4a16-ct` for root and both sub-agents (not 31B).
- Root agent: all 9 harness tools + two `agent_tool` sub-agents (`skip_summarization: true`).
- `code_analyzer` sub-agent: read-only locator, hard cap 6 tool calls, answer at most 12 lines, temp 0.2, thinking 2048.
- `patch_writer` sub-agent: writes exactly one candidate fix from a STRATEGY line, max 4 tool calls, max 2 `edit_file`, no testing, temp 0.6, thinking 1024.
- Root sampling: temp 0.2, top_p 0.95, `max_output_tokens` 16384, `thinking_budget` 4096, `include_thoughts: true`.
- One skill `skills/debug-loop/SKILL.md` (6-line reproduce-first loop). No evidence the model ever loads it.
- No adapter is wired in the committed `agent.yaml` (the adapters were trained, tested, and not adopted).

## Prompt summary (`agent/prompts/system.md`, 5.5 kB)

Phased best-of-N inside one session, paced by `get_status`:

- `f = agent_elapsed_seconds / (max_time_minutes x 60)`; constants `K_MAX = 3`, `LOCALIZE_SOFT = 0.25`, `SINGLE_PATH_AT = 0.50`, `VERIFY_STOP = 0.80`.
- Phase L: localize, write ONE repro at `/tmp/repro.py` that exits non-zero, pick the narrowest test command, no edits.
- If `f > 0.50` after localization: K=1 fast path (root patches itself, max 2 repair rounds).
- Else Phase C/V: call `patch_writer` 3 times with three fixed strategies (verbatim):
  - "Strategy 1, minimal: make the smallest change at the line where the wrong behavior happens."
  - "Strategy 2, root cause: fix the place where the bad value or state is first produced, even if that is a different function."
  - "Strategy 3, defensive: validate or normalize the input at the public entry point named in the issue."
- One-call candidate check that saves the diff, runs repro + tests, and resets the tree (verbatim):

```bash
cd /workspace && git add -N . && git diff > /tmp/cand_<K>.patch; echo DIFF_LINES=$(grep -c '^[-+][^-+]' /tmp/cand_<K>.patch); git diff --name-only | head -5; (timeout 30 python /tmp/repro.py > /tmp/repro_<K>.log 2>&1 && echo REPRO=PASS || echo REPRO=FAIL); timeout 60 <TEST_COMMAND> 2>&1 | tail -1; git reset -q; git checkout -q -- .; git clean -fdq
```

- Phase S ranking: eligible (non-empty, touches library code) > REPRO=PASS > more tests passed > smaller diff. Then `git apply /tmp/cand_<K>.patch` and `submit_patch`.
- Notable verbatim rules:
  - "The best one wins even if none has REPRO=PASS: a wrong patch scores the same as no patch, but a patch can still pass the hidden tests."
  - "When a tool response contains budget_warning (10 or fewer calls left), skip ahead immediately: apply the best saved candidate and submit"
  - "Never submit an empty diff or one that touches only test or config files."
  - "Keep thinking short and act: emit a tool call every turn until you submit."

## Runtime budgets (`agent/eval_config.yaml`)

`max_time_minutes: 4`, `max_tool_calls: 70`, `max_turns: 60`, `timeout_seconds: 120`, `verification_timeout_seconds: 300`.
Their reasoning: 12 h / ~120 tasks = 6 min/task including sandbox setup; 4 min x 120 = 8 h agent time leaves ~4 h for setup and vLLM start.

Measured facts that matter for budgeting (from `docs/experiments.md`):

- ~4.6 s per tool call on 12B (183 s / 40 calls), so 240 s is roughly 52 calls.
- With 40 tool calls the agent burned the whole budget exploring and never patched (`fastapi_15588`, diff=0). Raising to 70 calls plus an analyzer cap produced a patch in 13 calls.
- Average sample time sits at the cap in every run (3.98 min at a 4-min cap; 5.93 min at a 7-min cap; 3.6-3.8 min in the A/B). Time is the binding constraint for 12B, and raising the cap from 4 to 7 min barely moved the pass rate (5.8% to 7.5% sample pass).
- Running 4 concurrent sessions gave only ~1.3x effective parallelism (sandbox CPU contention).
- Running out of `max_turns` gives no `budget_warning`, unlike tool calls.

## Training (implemented and executed)

`scripts/train_lora_sft.py` (30 kB, with tests):

- LoRA r=16, alpha=32 (2 x rank), dropout 0.05, bias none, targets `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj`, CAUSAL_LM.
- lr 1e-4 cosine, warmup 1 step, batch 1, bf16, gradient checkpointing, `--max-len 8192`, default 2 epochs (real runs used 3).
- Trains on the unquantized twin (`google/gemma-4-12b-it`); 65.6M trainable params (0.545%); adapter 262 MB.
- Loss only on assistant turns flagged `patch_producing` (thought channel, tool calls, final content). System, issue and tool outputs masked. Supervised fraction ~16-21%.
- Chunked cross-entropy (lm_head + fp32 CE per 1024 positions under checkpointing) because full fp32 logits over a ~262k vocab at 8192 tokens (~8 GB) OOM one L4.
- Hand-ported Gemma 4 chat template renderer, byte-checked against `tokenizer.apply_chat_template`. Found that the HF tokenizer template differs from the Kaggle-mounted one.
- Export renames keys to the text-only layout (`model.layers.*`) that the vLLM Gemma4ForCausalLM override serves. Serve test with `adapter: sft_v1` passed with zero LoRA key errors.
- Practical environment notes: `pip uninstall -y torchao` is required for peft 0.19.1 on the Kaggle image; Quick Save does not persist `/kaggle/working`; L4x4 is only offered on competition-attached notebooks.

Data (`scripts/collect_trajectories.py`): n=4 samples per task at temperature 0.7 with distinct seeds, 25% deterministic holdout (`sha256(id) % 4 == 0`). "Multipath-consistent" filter:

- gold: at least 2 passing samples with the same normalized patch signature (whitespace-collapsed, headers dropped, sorted lines, sha256).
- silver: exactly 1 passing sample.
- dropped: 2+ passing but divergent.

Yield on 100 train tasks x 4 samples (400 runs, 7-min cap): 30/400 samples pass (7.5%), 16/100 tasks pass@4, **gold 5 tasks / 14 rows**, silver 9 tasks, 2 divergent dropped.

## Verification

- In-agent: repro script + narrowest test command + best-of-3 candidate ranking (prompt-only, commit `f063938`, the last commit).
- Offline: `scripts/verifier_select.py` is an executable mirror of the prompt policy that parses PACING and command blocks from `system.md` so the two cannot drift; tested against a fake harness with a real git sandbox. It never runs inside the scored agent.
- `scripts/build_submission.py`: zip validator (root agent.yaml, no symlinks, allowed extensions, 3 GiB), with tests.

## Evidence

| Claim | Value | Backing | Status |
|---|---|---|---|
| Unchanged starter (12B) public LB | 0.03 | Text in `docs/experiments.md`; author notes link to submission is "inferred from account + single entry + timing, not directly verified" | Asserted, self-flagged as indirect |
| 12B harness v1.1, 30 tasks x 4 | 7/120 samples, 2/30 tasks | Text log only; summary.json not committed | Asserted, detailed and self-consistent |
| 12B, 100 train tasks x 4, 7-min cap | 30/400 samples, 16/100 tasks pass@4 | Text log only | Asserted |
| Holdout A/B (29 tasks, n=2, 4 min) | base 2/58 (2/29), gold LoRA 0/58, gold+silver LoRA 1/58 | Text log; cites Kaggle notebook `cheeway/gemma4-ab-1?scriptVersionId=364924042`; includes a self-correction of a misread number | Asserted with external ref I could not open |
| Adapter hashes | sha256 values listed | Adapters not in repo | Unverifiable |
| Best-of-3 verifier (P3) effect | none reported | Last log line: "pending Kaggle holdout A/B" | Not measured |
| Any public LB score for the custom agent | none | No submission after the starter baseline is logged | Does not exist in repo |

No README claim exceeds the log. The README "Strategy" paragraph (LoRA + best-of-n wins) is a plan, and the log contradicts the LoRA half.

## Strengths

- Clean separation of plan vs measurement; self-corrections preserved.
- Real pipeline validation: train, export, package, serve inside the harness.
- Proper holdout split before training; A/B on unseen tasks.
- Concrete per-call latency and budget-binding observations.

## Weaknesses

- 12B was chosen on budget arithmetic, never compared with 31B. Their 12B local pass rate (~7%) is consistent with a low LB; the public evidence elsewhere (repo B: 31B single agent 0.17) suggests the model choice is the dominant factor.
- 14 gold rows (5 tasks, all from 4 repos) is far too little SFT data; the negative LoRA result is the expected outcome, and at n=29 it is also inside noise.
- The best-of-3 design triples patch-writing and adds sub-agent overhead inside a 4-minute cap where time is already binding. Unmeasured.
- Phase S ranks by the agent's own repro and existing tests, which do not include the hidden fail-to-pass tests.
- No custom-agent leaderboard submission recorded.

## Ideas worth adopting

1. **Deterministic holdout by id hash before any tuning** (`sha256(id) % 4`). Cheap, prevents scoring prompts or LoRA on their own tuning tasks.
2. **Label masking + chunked CE + byte-exact template check** if we train any LoRA. These are the three things that made training on L4s at 8192 tokens work, and the Kaggle-vs-HF template mismatch is a real trap.
3. **One-call CHECK_CANDIDATE command pattern** (diff save + repro + tail of tests in a single `run_command`). Useful even for a single candidate because it collapses 3-4 tool calls into one; tool calls and seconds are both scarce.
4. **`budget_warning` and time-fraction pacing rules**, and the fact that `max_turns` exhaustion gives no warning (set `max_turns` comfortably above `max_tool_calls`).
5. **"Submit the best candidate even if none reproduces"** rule: an empty diff is a guaranteed zero.
6. **Analyzer cap** (at most 2 calls, at most 6 tool calls inside) if a sub-agent is used at all; uncapped analyzer use consumed the whole budget.

## Ideas to reject

1. **12B as the main model.** Their own numbers are 6-7% locally and 0.03 on LB for the starter; nothing here shows 12B plus retries beats 31B.
2. **LoRA from self-collected passing trajectories at this data scale.** Measured null/negative (2/29 to 0/29 and 1/29). Only reconsider with an order of magnitude more data from a stronger teacher.
3. **Three-candidate patch_writer fan-out inside a 4-5 minute budget.** Unmeasured, and their own data says time is binding; a fan-out costs at least 3 sub-agent sessions plus 3 check calls.
4. **Requiring cross-sample patch convergence for "gold".** It cut usable rows from 30 passing samples to 14; with hidden-test-verified passes the convergence filter mostly throws away scarce data.
