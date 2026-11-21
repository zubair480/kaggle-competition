# E. rajrajak99/gemma4-tfd-agent (TFD-Agent, Kaggle discussion 745748)

- Discussion: https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745748 (rendered; author "Raja Rajak", shown as 51st in the competition at render time, posted ~2 months before 2026-11-21, 1 upvote, 0 comments).
- Links in the post: dataset `kaggle.com/datasets/rajrajak99/gemma-4-tfd-agentic-trajectories`, notebook `kaggle.com/code/rajrajak99/tfd-agent-autonomous-swe-bench-resolution-with-ge`, GitHub `github.com/rajrajak99/gemma4-tfd-agent`.
- Inspected commit: `67a45cf` (2026-09-30). 18 commits, one upload on 2026-09-27 and 17 on 2026-09-30.
- License: Apache 2.0 (copied to `configs/tfd-agent/LICENSE`).
- Size: 19 files, ~900 lines of Python including tests and demo, one PDF, one notebook.
- Verbatim copies: `configs/tfd-agent/` (`agent.yaml.txt`, `prompts.py.txt`, `benchmark_summary.csv`).
- Not inspected: the Kaggle dataset (50 trajectories) and the Kaggle notebook. Kaggle dataset download was not attempted beyond the page render; their contents are unverified.

## Verdict in one line

A Paper Track showcase, not a competition agent. The headline numbers are not backed by any run artifact, the benchmark CSV is internally inconsistent with the README and looks generated, the "agent" has no model call, and the `agent.yaml` is not in the competition's schema. Nothing here is usable as evidence.

## What is actually implemented

- `src/agent/loop.py` (77 lines): a `TFDAgent` class with a tool dispatcher and a JSON tool-call regex. **There is no run loop and no model call**; `model_client` is stored and never used.
- `src/agent/prompts.py`: one system prompt using `<start_of_turn>developer` tokens and a custom JSON tool-call format, plus a traceback-feedback template that keeps the last 1,500 characters of stderr and a "primary culprit" frame.
- `src/agent/verifier.py` (78 lines): writes a reproducer, runs it, parses the traceback for the last frame.
- `tfd_agent_demo.py` and the notebook: a scripted walk-through on an in-memory fake repository ("Isolated sandbox environment simulating repository file operations"), where the fix patch is **passed in as an argument** (`fix_patch={...}`). No LLM is involved.
- `src/training/qlora_train.py`: a generic 4-bit QLoRA script. r=16, alpha=32, dropout 0.05, targets q/k/v/o/gate/up/down, lr 2e-4, `max_steps=250`, batch 1 x grad-accum 8, `max_seq_length=4096`, base `google/gemma-4-31b-it`, data path `data/train_trajectories.jsonl` which does not exist in the repo. `dataset_prep.py` contains a "Sample synthetic seed trajectory". No adapter, no training log.
- `agent.yaml`: custom keys (`agent_name`, `model.name`, `lora.adapter_dir`, `execution.max_iterations: 30`, `timeout_seconds: 7200`, tools `view_file`, `search_code`, `run_bash`, `create_reproducer`, `context_window: 262144`). **This would not compile under the competition's ADK submission schema** and names tools that do not exist in the harness.

## Prompt summary

Five-step protocol: Understand & Locate, Reproduce (`reproduce_issue.py` that fails on the buggy code), Fix (minimal), Verify, Self-correct from the exact traceback. Notable verbatim line in the feedback template: "Please analyze the traceback in your <thought> tag, determine why your previous fix or reproduction was inadequate, and take corrective action." Generic; nothing harness-specific.

## Evidence

| Claim | Value | Backing | Status |
|---|---|---|---|
| "SWE-bench Lite 45.6% Pass@1" (TFD + QLoRA), 39.7% prompt-only, 29.5% ReAct, 18.2% zero-shot | README table and a notebook cell that hardcodes `pass_rates = [18.2, 29.5, 33.1, 39.7, 45.6]` | No run logs, no predictions file, no evaluation harness in the repo | **Unsupported** |
| `benchmark_summary.csv` "50 tasks" | CSV rows | Only **10 distinct task titles**, each repeated 5 times as "[Case #n]"; ids like `SWE-REQUESTS-1001` are not SWE-bench instance ids; includes repos that are not in SWE-bench Lite's naming (httpx, pydantic); CSV totals are baseline 10/50 (20%), ReAct 16/50 (32%), TFD **47/50 (94%)**, which contradicts the README's 39.7%/45.6% | **Looks synthetic and is inconsistent with the README** |
| "+16.1% absolute gain", "49.5% token reduction" | README | Derived from the above | Unsupported |
| QLoRA adapter exists | `agent.yaml` `lora.enabled: true` | No adapter, no training data in repo | Unsupported |
| 50 "clean multi-turn Gemma 4 trajectories" usable for SFT | Discussion post | Dataset not inspected; the post names tools `search_similar_code`, `get_code_neighbors`, `edit_file`, while the repo's own agent uses different tool names | **Unverified**; given the repo, treat as possibly synthetic until the files are read |
| Competition leaderboard score | none claimed | Author shown as 51st on the discussion page at render time; no link between that rank and this code | No attributable score |

## Strengths

- The reproduce-before-fix idea itself is sound and standard.
- Short, readable code.

## Weaknesses

- No executed agent, no model, no real repository, no evaluation.
- Numbers presented as benchmark results without artifacts; CSV contradicts README.
- Config incompatible with the competition harness.

## Ideas worth adopting

1. **Only the generic principle, and only as a hypothesis to test locally**: require the reproduction to fail before editing and pass after. Repos A and C implement the same idea in harness-valid form; use theirs.
2. **Traceback feedback shape** (last ~1,500 chars of stderr plus the innermost frame) is consistent with repo B's measured finding that tail-truncated tracebacks keep the pass rate while dropping tokens. Use B's evidence, not this repo's.

## Ideas to reject

1. **Using the 45.6% / 39.7% numbers for any planning.** Unsupported.
2. **Using the "50 trajectories" dataset as LoRA SFT data without reading every row.** If they are scripted or synthetic they would teach a tool vocabulary and turn format that does not match the harness (`view_file`/`run_bash` vs `read_file`/`run_command`, JSON-in-markdown tool calls vs native Gemma tool calls). Repo A's experience also shows that even genuine in-harness trajectories at this scale (14-23 rows) did not help.
3. **The `agent.yaml` layout and `<start_of_turn>developer` hand-written turn tokens.** Not the ADK schema; the harness applies the chat template itself.
4. **`max_seq_length=4096` for trajectory SFT.** Real harness trajectories are 5-10k tokens (repo A measured 41k tokens over 7 rows), so this truncates most of the supervised content.
