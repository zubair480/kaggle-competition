# E03: public baseline on 36 sound tasks (Kaggle 4xL4, sequential)

- Notebook: `gemma4-agent-baseline-36` (private).
- Config: `experiments/baseline/submission/` (public "Budget-Fit" family: 9 tools, 28 calls, 8 minutes, thinking 4096).
- Tasks: `experiments/sound_compare_36.txt` (all sound).

| Metric | Value |
|---|---|
| Resolved | 11 / 36 (31%) |
| Empty patch at the end | 4 / 36 |
| Duration per task | mean 273 s, median 264 s, p90 448 s, max 488 s |
| Tool calls per task | mean 21.8 |

## Paired with E02 (agent v2) on the 15 shared sound tasks

Baseline 6 / 15, v2 6 / 15. Five tasks pass in both; `fastapi_15589` passes only in the baseline,
`fastapi_5077` only in v2. No measurable difference at this sample size.

Empty patches on those 15: baseline 2, v2 4.
