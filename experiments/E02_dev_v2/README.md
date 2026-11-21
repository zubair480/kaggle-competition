# E02: agent v2 on 26 public tasks (Kaggle 4xL4, sequential)

- Notebook: `gemma4-agent-dev-v2` (private), official starter loop, pinned starter image.
- Config: `submission/` at commit 2f50889 (40 calls, 8 minutes, thinking budget 2048, 6 tools).
- Tasks: `experiments/dev_subset_26.txt`. 15 of them are sound (`data/sound_tasks.txt`).
- Per-task rows: `task_results.jsonl` (parsed from the notebook log).

## Measured

| Metric | Value |
|---|---|
| Resolved, sound tasks | 6 / 15 |
| Resolved, all 26 (11 cannot pass in this environment) | 6 / 26 |
| Empty patch at the end | 7 / 26 |
| Duration per task | mean 288 s, median 300 s, p90 470 s, max 488 s |
| Tool calls per task | mean 24.7 |
| Total agent time | 124.8 min |

## Reading

- Seven runs ended with no edit at all; five of those ran into the 8-minute cap with 24-30 calls used. The
  "edit by call 12" rule in the prompt was not followed in those runs.
- Mean duration of 288 s would put a 120-task run at about 9.6 h before per-task overhead. With hidden tasks
  likely harder, the 8-minute cap is not safe for the 12-hour limit.
- Single run, 15 sound tasks: the 95% interval on 6/15 is roughly 16%-68%. It ranks nothing by itself.
