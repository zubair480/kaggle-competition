# Public Kaggle notebooks: Gemma 4 Developer Agent Competition

Read-only analysis done 2026-11-21. Nothing from any notebook was executed; configs were extracted statically from notebook source.

## How this was collected

- Kaggle API `kernels/list?competition=gemma-4-developer-agent` paginated to the end: **1,028 public notebooks**.
- Source pulled for **188 notebooks**: the top 90 by votes, the top 110 by Kaggle's own `scoreDescending` order, and every title mentioning a score, LoRA/adapter, E2B/E4B/12B, skills, verifier, best-of-N or noise.
- Kaggle's public-score badges were read from the rendered competition Code tab sorted by score (151 notebooks carry a badge).
- Verbatim configs: [`kaggle_notebooks/<owner>__<slug>/`](kaggle_notebooks/) (51 folders, each with `NOTES.md`: source URL, badge, in-notebook score statements, byte-identical siblings).

## How to read the scores

Three kinds of evidence appear below, and they are labelled each time:

- **Badge**: the "Score" Kaggle prints beside a notebook on the Code tab. It is the notebook's best scored version, so it can belong to an older version than the source saved here.
- **Author statement**: a score written in the notebook text or title. Title-only scores are called title claims.
- **Repeat draws**: third-party notebooks that resubmitted byte-identical files several times.

Facts that set the scale, all from public notebooks:

- The public split is **58 tasks**; the board truncates to two decimals, so one task is 0.017. 0.22 = 13 tasks, 0.24 = 14 tasks (dariushafshar, carsonrodrigues, dmitriigluzdov).
- Byte-identical files re-score with a standard deviation of about **1.5 tasks** per draw, so about ±3 tasks at 95% (dariushafshar: pooled SD 1.56 over 29 draws; carsonrodrigues: 1.50, CI 1.18 to 2.04).
- Badge distribution across the 151 scored public notebooks: 0.22 ×4, 0.20 ×13, 0.18 ×23, 0.17 ×26, 0.15 ×16, 0.13 ×15, 0.12 ×12, lower ×42. **No public notebook has a badge above 0.22.**

## Comparison

All rows are `gemma-4-31b-it-qat-w4a16-ct` unless marked. "9 tools" = the six core tools plus the three graph tools; "6 tools" = `run_command, read_file, edit_file, write_file, get_status, submit_patch`. Budgets are `max_tool_calls / max_time_minutes / timeout_seconds / max_turns`. Sampling is temperature 0.2, top_p 0.95, max_output_tokens 8192, thinking_budget 4096, include_thoughts true unless noted.

| Implementation | Architecture | Training | Verification | Runtime budget | Evidence / claimed score |
|---|---|---|---|---|---|
| **verracodeguacas** [Budget-Fit Single Agent](kaggle_notebooks/verracodeguacas__gemma-4-agent-budget-fit-single-agent/) (248 votes) | Single agent, 9 tools declared, prompt forbids graph tools. "Edit by call 12", no new exploration after call 20. 4.7k-char prompt. | None | One targeted test or compile check, never a full suite, then `submit_patch`; confirm `patch_size > 0`. | 28 / 8 / 240 / 80 | Badge 0.18. **Repeat draws: mean 10.0 of 58 over 10 draws** (CI 8.98 to 11.02, dariushafshar); 8 to 11 over seven runs (dmitriigluzdov). Byte-identical forks carry badges 0.20 (leoprovorov score-to, xiuchisun). Local: 9/31 unseen-repo tasks (dmitriigluzdov). |
| **flexonafft** [Budget-Aware v2](kaggle_notebooks/flexonafft__gemma-4-budget-aware-coding-agent-v2/) (758 votes) | Same shell as Budget-Fit, 6.3k-char prompt: spec extraction with no tool call, batched `git grep -F`, call plan 1-8 / 9-12 / 13-20, edit-failure recovery via heredoc. | None | At most 2 verify calls: `timeout 150 pytest file -x -q -k kw`; `git diff` audit against the issue's literal names. | 28 / 8 / 240 / 80 | Badge 0.22 (13/58, first run of V10). **Repeat draws of the same files: 7, 7, 8, 9, 10, 10, 10 (mean 8.7)** (dariushafshar). Source docstring: "Our SuperAgent adaptation scored 0.18 … This candidate has not been scored." Local: 9/31 (dmitriigluzdov). |
| **honghanhhh** [Gemma 4 Baseline](kaggle_notebooks/honghanhhh__gemma-4-baseline/) (77 votes; formerly titled "LB 0.24") | flexonafft v2 with three prompt edits: protect `pytest.ini`/`conftest.py` and keep scratch in `/tmp`; apply the change to every parallel implementation (sync/async, overloads, `__all__`); final check is `git status --short && git diff`. | None | As flexonafft, plus untracked-file check before submit. | 28 / 8 / 240 / 80 | **0.24 is a title claim** by the author, repeated by forks. Badge today: 0.18. Byte-identical resubmissions: runtime exceeded (alexust); runtime exceeded twice (carsonrodrigues); forks with badges 0.20, 0.18, 0.17, 0.15. With one extra prompt line: 0.17; with a 7-minute cap: 0.15 (alexust). |
| **bliverrigpdoge** [LB 0.22, 3 tweaks](kaggle_notebooks/bliverrigpdoge__lb-0-22-3-tweaks-40-tool-calls-no-training/) (114 votes) | Budget-Fit plus: 40 calls; reply "Done" after `submit_patch`; submit at once when the call budget is exhausted; **issue text pinned at the end of the system prompt with `{problem_description}` and `{hints?}`** so it survives compaction. | None | As Budget-Fit. | **40** / 8 / 240 / 80 | Title claim 0.22; badge 0.22. One draw. alexust's own 40-call / 8-minute bundle exceeded the runtime limit. |
| **denpugovkin** [Repair Lab](kaggle_notebooks/denpugovkin__gemma-4-repair-lab-compare-before-you-submit/) (158 votes), control bundle = exp021 | 6 tools, Patchsmith prompt (4.9k chars): contract extraction, one narrow literal search, 80-120 line reads, edit within 6-8 calls, "do not manufacture a cosmetic patch". | None | Keep 4 calls and 75 s in reserve; `py_compile` after the **last** edit chained with one focused behaviour check; direct Python assertion when pytest is disabled; diff against `_swegemma_baseline`. | 28 / 8 / **60** / 80 | Author statement: "exp021 public 0.22, Version 5"; badge 0.22. Same author: exp023 (larger output cap) 0.12, exp024 (extra verification paragraph) 0.12, status-policy trial 0.17. The root bundle in the notebook is an **unscored** 40-call candidate. |
| **hanifnoerrofiq** [Patchsmith](kaggle_notebooks/hanifnoerrofiq__patchsmith-gemma-4-developer-agent/) (21 votes) / **evgendvorkin** [reproduction](kaggle_notebooks/evgendvorkin__can-gemma-4-become-a-software-engineer/) (55 votes) | Origin of the Patchsmith prompt. Current V11 = 40 calls. evgendvorkin's bundle is byte-identical to denpugovkin's exp021 control. | None | As above. | 40 / 8 / 60 / 80 (V11); 28 / 8 / 60 / 80 (reproduction) | Badges 0.20 and 0.20. evgendvorkin: "historical best 0.20", later versions 0.15 and 0.17. V11: "No score or full-workload runtime has been measured". |
| **ayush04barai** [Version 1 added Adaptor](kaggle_notebooks/ayush04barai__version-1-added-adaptor/) (115 votes) | Budget-Fit-style prompt, 9 tools, `adapter: main_lora`, max_output_tokens 6144. | **LoRA r16 / alpha 16, layers 30-59, q_proj + o_proj + down_proj, lr 2e-4, 4 h on L4, NF4 4-bit over `gemma-4-31b-it-qat-q4_0-unquantized`.** Loss only on `edit_file` calls on source files from resolved runs (Gemma and Qwen trajectories from dataset `dmitriigluzdov/gemma-4-serving-and-lora-verification-kit`). | As Budget-Fit. | 28 / 8 / 240 / 80 | Badge 0.22, but the notebook says the same files **without** the adapter range "0.12 to 0.22" and gives no score for the adapter version. The LoRA's effect is unmeasured. |
| **navyadevadiga** [T8 static](kaggle_notebooks/navyadevadiga__gemma4-swe-agent-t8-static/) (76 votes) | **3 tools** (`run_command, read_file, submit_patch`); edits by Python heredoc with a count-equals-one assertion. Temperature 0.3, top_k 64, **thinking_budget 256**. "Never write a backtick in a command." | None | Reproduce the issue's example or run the module's own test file, at most two fix attempts. | 25 / 8 / 240 / **40** | Author statement: **0.20 on 2026-10-23, then 0.15 for the identical version on 2026-10-28**. With a 4-minute cap the same agent scored 0.15. Badge 0.20. |
| **flexonafft** [Short-Prompt](kaggle_notebooks/flexonafft__gemma-4-budget-aware-short-prompt/) (34 votes) | 6 tools, **1.5k-char prompt**, thinking_budget 1024. Rationale: compaction at about 14k tokens happens in most tasks. | None | At most 2 verify calls. | 28 / **10** / 240 / 80 | Badge 0.20. Docstring: the base (long prompt, thinking 1024, 10 min) scored 0.17. |
| **jvnhonglei** [SuperAgent Reproduction](kaggle_notebooks/jvnhonglei__gemma-4-superagent-reproduction/) / **matterhorn3838** [SuperAgent](kaggle_notebooks/matterhorn3838__gemma-4-superagent/) | Budget-Fit shell with an issue-contract prompt; ancestor of flexonafft v2. | None | Targeted test. | 28 / 8 / 240 / 80 | Badges 0.20 and 0.17. Identical files drew 8 and 12 of 58 (dmitriigluzdov). |
| **davis0178** [Agent Baseline](kaggle_notebooks/davis0178__gemma-4-agent-baseline/) (= shimauchu v19, victorzhong six-tools) | 6 tools, 4.0k-char prompt. | None | Targeted test. | 28 / 8 / **300** / 80 | Badges 0.17, 0.20 and 0.18 for byte-identical bundles. |
| **yiyu0716** [v19](kaggle_notebooks/yiyu0716__g4-pack-yiyu-v19-fixed-trace-t7p5/) | Coder (4 tools) + analyzer workflow sub-agent + **ADK skill `g4-edit` shipping Python scripts** (SEARCH/REPLACE editor with syntax check, `--trace`, `--check`) run through `run_skill_script`. Temperature 1.0, max_output_tokens 2048, include_thoughts false. | None | `g4edit.py --check` restores test files, deletes scratch files, names the closest tests. | **100** / 7.5 / 300 / 120 | Badge 0.17 (also cited as 0.17 by hitarthjain0). |
| **kevlarzanderchi** [Mega Ensemble](kaggle_notebooks/kevlarzanderchi__0-22-mega-ensembl/) | flexonafft bundle + skill `code-tools`: `locate.py` (rarity-weighted `git grep` localizer) and `check.py` (compile, closest test, diff stat). | None | `check.py` after the edit. | 28 / 8 / 240 / 80 | Badge 0.18. Author calls it unmeasured. |
| **boristown** [E2B LoRA … Baseline](kaggle_notebooks/boristown__gemma-4-e2b-lora-fine-tuning-swe-agent-baseline/) (72 votes) | 31B despite the title, 5 tools, thinking 2048, max_output_tokens 4096. | "Surgical" LoRA: r8 / alpha 2, q_proj + o_proj on layers 48-59 only. | Targeted test. | 36 / 7.5 / 240 / 80 | Author statement: "V21 (21/60, LB 0.15-0.17)"; badge 0.17. Local 60 tasks on 4×L4 took about 5.5 h. |
| **spiritofvishwakarma** [agent1](kaggle_notebooks/spiritofvishwakarma__gemma4-agent1/), [agent2](kaggle_notebooks/spiritofvishwakarma__gemma4-agent2/) | Starter shape: coder + analyzer sub-agent, sample adapters declared, temperature 0.9. | Sample adapters only | Starter | defaults / timeout 150 or 60 | Badges 0.18 and 0.18. |
| **zhukovoleksiy** [Walkthrough](kaggle_notebooks/zhukovoleksiy__gemma-4-walkthrough-findings-submission/) (101 votes) | Coder + analyzer, 9 tools, temperature 1.0. | None | Starter | 28 / 7 / 240 / 80 | Badge 0.15. |
| **romanrozen** "LB TOP 1" (261 votes, bundle built from `sample_submission` at run time, not extractable) | Analyzer + coder, graph tools, no `eval_config` budget. | None | Starter | Harness defaults | Title claim; 0.12 as the author's report. Identical files drew 4, 6 and 7 of 58 (dmitriigluzdov). |
| **E4B small-model bundles**: [fernandosr85](kaggle_notebooks/fernandosr85__gemma-4-e4b-budget-aware-swe-agent/), [kawh1111 v4](kaggle_notebooks/kawh1111__g4-e4b-v4/), [apihpih](kaggle_notebooks/apihpih__gemma4-e4b-locate-check-submit-v1/) | The 31B single-agent bundles with `model: gemma-4-e4b-it-qat-w4a16-ct`, 6 tools. | None | Same | 28 / 8 / 240 / 80 (apihpih: 30 / 3.5 / 180) | Badges 0.06 (kawh1111 v4, apihpih). dheerajpiduru: six E4B runs all 3 to 5 of 58. carsonrodrigues: E4B reads 4 and 5 of 58. Official small-model board (2026-10-20 snapshot): top score 0.06. |

Notebooks that train adapters but publish no bundle score:

| Notebook | Recipe | Reported result |
|---|---|---|
| verracodeguacas, "31B Agent LoRA: Short-Thought Trainer" | TPU v5e-8, JAX/Tunix/Qwix, r16, lr 5e-5, 2 epochs. On-policy data: the agent's own runs that passed hidden tests, segmented exactly as the harness compacts them (pre- and post-compaction segments, summaries written by 31B itself). Loss only on turns whose thought is at most 1,500 characters. Arm b: only runs solved within 14 tool calls. | Stated in the follow-up notebook: "that adapter solved **25 vs 18 of 71 held-out tasks** over the base model, with timeouts down from 38 to 24" (local, 24 calls / 8 min). No leaderboard score. |
| verracodeguacas, "In-Step Teacher Preferences" | Stage 2: Gemini 3.8 Flash labels 1,000 of the agent's own decision points; in-step DPO plus SFT versus SFT only. | Training notebook; no resolve-rate result stated. |
| verracodeguacas, "Pruned Model Teacher Healing" | 30% of MLP channels pruned, KD from the full model through a r16 LoRA. | "about 15% faster", +0.08 nats per token before healing. No score. |
| scottweeden, "Tool LoRA Writeup" | r16 on all 410 projections, 83 of the model's own resolved turns (14 tasks). | Base bundle 14/48 on a held-out Rich fold; "Its resolve-rate run is pending". Caps sessions at 6 minutes after measuring 8 minutes at 12.4 to 14.2 h for 120 tasks. |
| dheerajpiduru, "E4B: what moved the score" | E4B LoRA distilled from 31B trajectories of the same agent. | Validation loss 0.49 to 0.35, but **3 solves in 87 runs versus 6 for plain E4B**; "kept exploring and often never submitted". Not submitted. |
| denpugovkin, "31B QLoRA Study" | Unified-diff SFT from public fixes, Rich held out. | Loss only; "not a solved-issue score". |

## What the highest-scoring credible configs have in common

1. **One 31B agent, no sub-agents, no skills, no adapter.** Every bundle with a badge of 0.20 or more is a single `gemma-4-31b-it-qat-w4a16-ct` agent. The one 0.22-badge notebook that ships a LoRA says its no-adapter files already ranged 0.12 to 0.22.
2. **The same budget: 28 tool calls, 8 minutes, 80 turns.** 12 of the 17 notebooks with a badge of 0.20 or more use 28 calls and 8 minutes; the exceptions are 25, 30 or 40 calls, or 10 minutes.
3. **The same sampling: temperature 0.2, top_p 0.95, max_output_tokens 8192, thinking_budget 4096, include_thoughts true.** Ayush Thakur's 129-task ablation, as copied by hitarthjain0: reference 48 solved; temperature 0.0 / 0.4 / 1.0 gave 47 / 51 / 51; thinking budget 2048 / 6144 gave 50 / 48; **summaries off 35 (against 51); thinking disabled 23**.
4. **A forced early edit.** "By your 12th tool call you must have edited a source file", backed by the fact that the working tree is graded even without `submit_patch` and an empty diff scores zero.
5. **Issue text as a literal contract.** Exact names, messages, exception types and status codes copied from the issue.
6. **Diff hygiene.** Never touch tests, scratch files in `/tmp`, never run a full suite, wrap test runs in `timeout`, check the diff before submitting.
7. **Graph tools unused.** Either unregistered or forbidden in the prompt. Reported reasons: all 21 semantic searches in a 129-task run returned nothing (hitarthjain0 citing Ayush Thakur), and declaring any graph tool makes the harness append a "Code Intelligence Tools" section telling the model to use them (xingling666, citing `agent_runner.py`).

The practical summary from the repeat-draw notebooks: **the public top configs are one agent measured many times.** The four file sets with three or more draws average 9.25 to 10.0 of 58, a spread smaller than one draw's noise. The 0.22 and 0.24 figures are the upper tail of a config whose mean is about 0.16 to 0.17.

## Differences that plausibly matter

Ordered by how much evidence backs them.

1. **Total runtime is the binding constraint, and the popular 8-minute config sits on the 12-hour edge.** Byte-identical "0.24" files produced 0.24, 0.17 and "exceeded the allowed runtime" (alexust), and two more runtime failures (carsonrodrigues). alexust's projection from 101 timed local runs puts 28 calls / 8 minutes at about 12 h for 120 tasks, and a 7-minute cap at about 40 minutes of margin for at most one lost task in 30. scottweeden measured 12.4 to 14.2 h at 8 minutes and chose 6. dmitriigluzdov projects 11.6 to 12.0 h. Raising calls to 40 at 8 minutes timed out for alexust.
2. **Model size.** 31B against E4B with everything else equal: about 6 tasks of 58 (carsonrodrigues, the only change in 15 that cleared his noise threshold). 12B with the Budget-Aware bundle exceeded the 12-hour limit and solved 3 or 4 of 31 locally against 9 and 11 for 31B (dmitriigluzdov).
3. **Thinking and thought summaries on.** The only large, replicated sampling effect (item 3 above).
4. **History compaction.** The harness compacts once a prompt reaches 14,336 tokens and afterwards the original task message is gone; the first compaction comes around the 14th tool call and about half of all steps happen after it; repeated tool calls roughly triple afterwards (verracodeguacas). Three public responses exist: pin the issue into the system prompt with `{problem_description}` (bliverrigpdoge, badge 0.22, one draw); shorten the prompt and tool list (flexonafft short-prompt, badge 0.20); train an adapter on post-compaction segments (verracodeguacas, 25 vs 18 of 71 locally). None has a repeated leaderboard measurement.
5. **`max_output_tokens` 8192, not the sample's 16384.** vLLM runs at `max_model_len` 32768 and refuses any call where prompt plus requested output exceeds it; with 16384 a prompt above 16,384 tokens ends the task with no patch (dariushafshar, 1 of 7 traced tasks). denpugovkin's "larger output ceiling" experiment scored 0.12 against 0.22 for its parent.
6. **Tool-call cap.** Cutting 50 to 25 calls cost 14 of 129 locally (Ayush Thakur via hitarthjain0), while 28 to 40 on the leaderboard has one good draw (bliverrigpdoge) and one timeout (alexust). More calls help resolution and cost wall-clock time.
7. **Command timeout 60 s against 240 s.** The Patchsmith line uses 60 s and holds a 0.22 author statement; nobody has isolated it. A lower value also bounds the worst case of one hung command.
8. **Tool count.** 3, 6 and 9 tools all appear at badge 0.20. xingling666's cohort comparison finds tools, thinking budget and call count all inside noise.
9. **Adapters.** The only positive resolve-rate number is local (verracodeguacas, on-policy, short-thought, compaction-aware). The only negative one is E4B distillation from 31B (worse than base). Common training base: Kaggle model `google/gemma-4`, Transformers variation `gemma-4-31b-it-qat-q4_0-unquantized` version 2, so the adapter matches the served w4a16 model.
10. **Skills with scripts.** Allowed (`run_skill_script`); the two public examples have badges 0.17 and 0.18, no better than prompt-only bundles.

Findings that limit what any config can reach:

- dominyellow (6,187 task-runs, 46 variants): only one variant beat the baseline locally, and it timed out on Kaggle. Giving the same agent progressively more specific hints moved it from 12 to 41 of 47 hard tasks: "The model can write the code. What it cannot do is know what the maintainers decided."
- carsonrodrigues: a 74-task local screen did not rank his hidden reads; hidden tasks come from other repositories than the public ones.
- A model call costs about 16.7 s plus 0.139 s per generated token on the scorer-like setup (verracodeguacas); for 12B, 17.25 tokens/s and 76% of wall-clock is generation (xingling666).
- Harness details reported in prompts and audits: `get_status` and `submit_patch` do not consume the call budget; `budget_warning` is only emitted when `max_tool_calls` is at least 20; the harness loop ends on `submit_patch`; the competition sandbox may disable pytest (Patchsmith prompt).

## Starter notebook: how submission and local eval work

Source: [`kaggle_notebooks/ryanholbrook__getting-started-gemma-4-developer-agent/notebook_cells.txt`](kaggle_notebooks/ryanholbrook__getting-started-gemma-4-developer-agent/notebook_cells.txt).

**Notebook settings.** GPU on (machine shape `NvidiaL4`; community notebooks describe it as L4 ×4), internet off. Inputs: the competition data, dataset `metric/gemma-4-developer-agent-wheelhouse`, and model `google/gemma-4`, variation `Other`, `gemma-4-{31b,12b,e4b,e2b}-it-qat-w4a16-ct`, version 2 (mounted at `/kaggle/input/models/google/gemma-4/other/<model>/2`).

**Wheelhouse.** Dataset `metric/gemma-4-developer-agent-wheelhouse`, **version 31**, last updated 2026-10-12, 41 wheels (cp312), 881 MB. Key pins:

| Package | Version |
|---|---|
| swegemma | 0.2.11 |
| adk_submission | 0.2.13 |
| adk_eval_core | 0.1.0 |
| google_adk | 1.36.1 |
| google_genai | 2.11.0 |
| vllm | 0.19.1 |
| transformers | 5.13.1 |
| tokenizers | 0.22.2 |
| safetensors | 0.8.0 |
| compressed_tensors | 0.15.0.1 |
| bitsandbytes | 0.46.1 |
| flashinfer_python / flashinfer_cubin | 0.6.6 |
| xgrammar | 0.2.5.post1 |

Install: symlink the wheels into `/tmp/wheelhouse` restoring the `+cu128` local version tag that Kaggle strips, skip `cutlass` wheels and delete broken `*cutlass*.pth` files, then `pip install -q --no-deps --force-reinstall *.whl`.

**Bundle.** The starter copies `sample_submission/` from the competition data to `/kaggle/working/sample_submission`. Default `MODEL_NAME` in the notebook is `gemma-4-12b-it-qat-w4a16-ct`; for any model other than 31B it rewrites every `model:` line and deletes `adapter:` lines and the `adapters/` folder, because the sample adapters are 31B-shaped dummies. Exactly one base model may be declared.

**vLLM launch** (`adk_submission.VllmConfig` + `VllmServer`):

- `tool_call_parser='gemma4'`, `reasoning_parser='gemma4'`, `enable_auto_tool_choice=True`
- `max_model_len=32768`, `gpu_memory_utilization=0.90`, `dtype='bfloat16'`
- `tensor_parallel_size` 4 with four GPUs (2 with two, else 1), `startup_timeout` 20 minutes
- `enable_lora` when adapters are found, `max_loras = number of adapters`, `max_lora_rank` = largest detected rank (128 when none)
- 12B only: `--hf-overrides '{"architectures": ["Gemma4ForCausalLM"], "model_type": "gemma4"}'`
- Model registry for ADK through LiteLLM: `create_model_registry(aliases=[model], model_prefix='openai/', api_key='EMPTY')`, `litellm.drop_params = True`
- Environment: `VLLM_WORKER_MULTIPROC_METHOD=spawn`, `VLLM_ENGINE_READY_TIMEOUT_S=1200`, `TRANSFORMERS_OFFLINE=1`, `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, OTEL disabled

**Local eval on public tasks.** `swegemma.evaluate.Evaluator(EvalConfig(...))`, then `evaluator.evaluate_task(task=..., task_index=..., total_tasks=...)` per task (async; the starter runs two tasks, `tasks[:2]`). Settings:

- `tasks_path = tasks.jsonl`, `snapshots_dir`, `graph_dir`, `embeddings_dir`, `wheels_dir` from the competition data; `sandbox='subprocess'`
- Budgets read from the bundle's `eval_config.yaml` (`evaluation:` section) with starter defaults `timeout_seconds 300`, `verification_timeout_seconds 300`, `max_tool_calls 100`, `max_time_minutes 60`, `max_turns` unset
- `limits, generation_constraints = build_submission_limits()`
- `ContextCacheConfig(min_tokens=2048, ttl_seconds=1800, cache_intervals=10)`
- `EventsCompactionConfig(compaction_interval=15, overlap_size=2, token_threshold=14336, event_retention_size=5)`
- Result fields: `resolved`, `test_exit_code`, `agent_patch`, `tool_calls`, `duration_seconds`

Community caveats for local grading: with `sandbox='subprocess'` the test dependencies are not installed and the sandbox sees every Kaggle package, so zbigniewkirchner builds a clean Python 3.13 / pytest 8.4.2 venv per task and reports gold patches passing on 127 of 129 public tasks; dmitriigluzdov and matterhorn3838 report 114 sound tasks of 129 after empty-patch and gold-patch controls. A 60-task run on 4×L4 took about 5.5 h (boristown); 12 tasks × 2 bundles took about 2 h (zbigniewkirchner).

**Packaging.** `validate_directory(AGENT_DIR, limits=limits)`, no symlinks, then `shutil.make_archive('/kaggle/working/submission', 'zip', root_dir=AGENT_DIR)` so `agent.yaml` is at the archive root. Checks: total size at most `MAX_SUBMISSION_SIZE_BYTES` (3 GiB), every file extension in `ALLOWED_SUBMISSION_EXTENSIONS`. Most community notebooks skip all of this: they run on CPU with internet off and write the four text files straight into `submission.zip` with the standard library, which avoids any failure during Kaggle's re-run of the notebook.

**Submitting.** Notebook statements differ: navyadevadiga says Kaggle re-runs the notebook at scoring time and grades the zip that re-run produces; denpugovkin advises downloading `submission.zip` from the notebook output and using the File Upload tab because a notebook re-run can time out. Reported limits: about one scored submission a day, one pending at a time since 8 October, queues of 12 to 46 hours (hitarthjain0, zbigniewkirchner).

## Analysis notebooks worth reading in full

| Notebook | Use |
|---|---|
| dariushafshar/gemma-4-most-run-public-config-averages-10-58 | Repeat draws per exact file set; dataset `dariushafshar/gemma-4-agent-public-config-draws`. |
| alexust/one-bundle-three-outcomes-0-24-0-17-no-score | Runtime projection for 8, 7 and 6-minute caps. |
| carsonrodrigues/27-hidden-reads-what-moved-the-score-what-didn-t | 27 submissions scored against a noise model. |
| dmitriigluzdov/gemma-4-public-agent-ideas-and-evidence | Catalogue of 187 notebooks, paired 31-task screen, 12B timing failure. |
| hitarthjain0/gemma-4-agent-what-took-lb-0-12-0-24 | Summary of Ayush Thakur's ablations (discussion 746250). |
| verracodeguacas/gemma-4-31b-agent-lora-short-thought-trainer | Compaction mechanics and the only adapter recipe with a positive local result. |
| dominyellow/19-days-6-187-runs-0-18-a-win-i-couldn-t-submit | 46 variants, hint-ladder diagnostic. |
| xingling666/same-8-minutes-scores-from-0-05-to-0-20 | Settings the harness ignores. |
| zbigniewkirchner/gemma-4-agent-run-your-agent-locally | Scorer-like paired local eval on 4×L4. |
| ryanholbrook/gemma-4-developer-agent-small-model-leaderboard | Official Small Model Prize board (pinned). |
