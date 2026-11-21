# E04: agent v3 at a 5-minute cap, 36 sound tasks (Kaggle 4xL4, sequential)

- Notebook: `gemma4-agent-v3-sound36` (private). Config: `submission/` (this is the shipped configuration).
- Tasks: `experiments/sound_compare_36.txt`. Rows: `task_results.jsonl`. Failure classes: `../failure_analysis.csv`.

| Metric | Value |
|---|---|
| Resolved | 12 / 36 (33%); FastAPI 7/18, Rich 5/18 |
| Duration per task | mean 217 s, median 221 s, p90 306 s, max 515 s |
| Agent timed out (harness warning) | 8 / 36; none of those resolved |
| Empty patch | 9 / 36 |
| Tool calls per task | mean 19.2 |

One task (`rich_3772`) ran 515 s under a 300 s cap; the same task overran in E05 (606 s), so a single command
can overrun the cap by minutes. The per-task trace digest printed empty in this run (filter bug, fixed after).
