# Gemma 4 agent runs

Per-task outcomes of every practice run behind the writeup *Git History as a Gym: Verified Practice Tasks for a 4-bit
Gemma 4 Coding Agent* (Gemma 4 Developer Agent paper track), with the agent configurations and LoRA training logs, so every
number in its tables and figures can be recomputed.

All runs used the official harness (swegemma) on Kaggle 4xL4 machines with the competition model
`gemma-4-31b-it-qat-w4a16-ct` (v22b: `gemma-4-12b-it-qat-w4a16-ct`), one task at a time unless noted.

## Files

| File | Contents |
|---|---|
| `runs.jsonl` | One line per run and task: `run`, `agent`, `set` (dev, dev2, dev40, practice, heldout66), `task`, `resolved`, `tool_calls` (as the harness counts them; the cap is in each agent's `eval_config.yaml`), `seconds`, `steps` (model steps), `first_edit_s`, `first_edit_step` (1-based model step of the first source edit), `calls_by_kind` (tool calls classified as read, search, edit, edit_cmd, pytest, script, scratch_write, submit, git, cmd, get_status, locate), `output_tokens`, `compactions`, `empty_patch` |
| `agents/<version>/` | The declarative agent bundles as submitted: `agent.yaml`, prompts, sampling and evaluation budgets |
| `training/*.metrics.json` | TPU LoRA runs: configuration, validation loss per checkpoint, step times |
| `leaderboard.json` | Our public leaderboard scores per submitted version (58 public tasks; one task = 0.017) |

Task sets: `dev` and `dev2` are two disjoint sets of 23 public tasks whose reference fix passes in the participants'
sandbox (see the gold-patch census in the LocBench-129 dataset); `dev40` is an earlier 40-task split of all public tasks.
`practice` is one attempt of v25 on each of the 366 Git History Gym tasks (four at a time, 12-minute cap); `heldout66`
is the 66 Jinja and Typer practice tasks excluded from self-training, run four at a time with a 12-minute cap.
The practice and heldout66 task ids refer to the Git History Gym dataset. v29 and v37 exceeded the scorer's time
limit and have no leaderboard score.

**Not included:** issue texts, patches, test patches, snapshots and agent transcripts. Those are competition data or
derived from it; task ids refer to the competition's public tasks.

## License

Apache License 2.0.
