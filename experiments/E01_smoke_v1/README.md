# E01: GPU smoke test of agent v1

- **Hypothesis:** the submission compiles, serves and produces patches on the real Kaggle stack (4x L4, vLLM 0.19.1, official image).
- **Config:** agent v1 (commit c393f4a): gemma-4-31b, 6 tools, 5 min / 40 calls / 60 turns, temperature 0.4, thinking 2048.
- **Tasks:** 6 public tasks with the smallest reference patches (2 per main repo). Chosen to be easy; this is not a pass-rate estimate.
- **Result:** 4/6 resolved. Whole notebook took 24.6 minutes including wheel install and vLLM start.
- **Per task:** see `task_results.jsonl` (parsed from the Kaggle notebook log).
- **Conclusion:** pipeline works end to end; private Kaggle notebooks are a usable evaluation path.
