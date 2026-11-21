# E05: public baseline at a 5-minute cap, 36 sound tasks (Kaggle 4xL4, sequential)

- Notebook: `gemma4-agent-baseline5-sound36` (private). Config: `experiments/baseline_5min/submission/`
  (E03 config with `max_time_minutes: 5` and the prompt's "8 minutes" changed to "5 minutes").
- Same tasks as E04.

| Metric | Value |
|---|---|
| Resolved | 12 / 36 (33%); FastAPI 7/18, Rich 5/18 |
| Duration per task | mean 245 s, median 252 s, p90 307 s, max 606 s |
| Agent timed out | 10 / 36 |
| Empty patch | 7 / 36 |
| Tool calls per task | mean 20.3 |

Paired with E04: 11 tasks resolved by both; `fastapi_11194` only here, `fastapi_14616` only in E04.
