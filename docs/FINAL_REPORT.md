# Final report

Date: 2026-11-21. Deadline for final submissions: 2026-12-02 23:59 UTC.

**Status: `submission.zip` is built, validated and smoke-tested. It has not been submitted to Kaggle**, because
the available API token lacks the `competitions.participate` permission. There is no leaderboard score.

Every number below is marked **Measured** (this project ran it), **Reported** (from other participants or
staff) or **Hypothesis**.

## 1. Best architecture

A single agent with six tools (`run_command`, `read_file`, `edit_file`, `write_file`, `get_status`,
`submit_patch`), one system prompt with the task statement pinned at its end, thinking enabled, and a budget of
30 tool calls and 5 minutes per task. Details: `docs/ARCHITECTURE.md`.

"Best" here means: tied with the alternatives on resolved tasks, and the fastest of them (Measured, item 14).

## 2. Best model variant

`gemma-4-31b-it-qat-w4a16-ct`. Only this variant was run in this project. Reported: E4B scores about
0.05-0.06 on the public leaderboard; 12B submissions exceeded the 12-hour limit.

## 3-10. Measured performance of the shipped configuration (E04)

One run, Kaggle 4xL4 notebook, official harness, tasks run sequentially.

| # | Item | Value |
|---|---|---|
| 3 | Pass rate | 12 / 36 = 33% (95% interval roughly 19%-51%) |
| 4 | Tasks evaluated | 36 sound public tasks |
| 5 | Per repository | FastAPI 7 / 18, Rich 5 / 18 |
| 6 | Average runtime per task | 217 s |
| 7 | Median runtime | 221 s |
| 8 | 90th-percentile runtime | 306 s |
| 9 | Timeout rate | 8 / 36 = 22% hit the 5-minute cap; none of them resolved |
| 10 | Tasks completed | 36 / 36 produced a result; 27 produced a non-empty patch |

Projected scorer time for 120 tasks (Hypothesis, from the measured mean plus about 30 s overhead per task):
about 8.2 hours. If every task ran to the cap: about 11.3 hours. Both are under the 12-hour limit.

**This pass rate will not transfer to the leaderboard.** The 36 tasks come from two public repositories and
exclude tasks the public environment cannot verify. Reported public-set rates of 35-43% correspond to
leaderboard scores of 0.16-0.24.

## 11. Retrieval performance

Measured, model-free, 129 tasks (`docs/RETRIEVAL_RESEARCH.md`): gold file in the top 5 for 47% with identifier
grep, 54% with BM25, 35% with the harness's graph similarity tool, 59% with all three fused.

Measured, end to end (E04): of 27 runs that produced a patch, 24 edited at least one file that the reference
fix edits.

## 12. Verification performance

Measured (`docs/EVALUATION_INTEGRITY.md`): on the official Kaggle image the reference patch passes for 74 of
129 public tasks and an empty patch passes for 3, leaving 71 sound tasks.

The agent has no separate verifier. Its in-task self-check was not measured in isolation.

## 13. LoRA performance

Not measured. No adapter was trained: this environment has no GPU, and the Kaggle GPU quota went to
evaluation. Reported: no public evidence that an adapter improves the score.

## 14. Comparison against the official baseline

The official sample submission was not run on GPU. The comparison below uses the strongest measured public
configuration instead (item 15).

## 15. Comparison against reproduced competitor approaches

Measured, same 36 sound tasks, one run each.

| Configuration | Resolved | Mean time | Timed out | Empty patches |
|---|---|---|---|---|
| **Agent v3, 5 min, 30 calls (shipped)** | 12 / 36 | 217 s | 8 | 9 |
| Public "Budget-Fit" baseline, 5 min, 28 calls | 12 / 36 | 245 s | 10 | 7 |
| Public "Budget-Fit" baseline, 8 min, 28 calls | 11 / 36 | 273 s | 3 | 4 |
| Agent v2, 8 min, 40 calls (15 sound tasks only) | 6 / 15 | 288 s | 2 of 15 | 4 of 15 |

Nine tasks are resolved by all three 36-task runs. The differences (one task) are inside run-to-run noise;
Reported noise for identical files on the leaderboard is 2-5 tasks.

**The shipped agent is not measurably better than the public baseline at resolving tasks.** Its measured
advantage is time: 11% faster than the baseline at the same cap, 21% faster than the 8-minute baseline.

## 16. Most important discoveries

1. Measured: only 71 of 129 public tasks can be used to measure anything in a Kaggle notebook.
2. Measured: three different prompt and budget configurations resolve the same tasks. Prompt wording and
   three extra minutes changed nothing measurable.
3. Measured: success tracks fix size. Resolved tasks have a median reference fix of 5 lines; failed ones 20
   or more. File localization is right in 24 of 27 patched runs.
4. Measured: the code-graph similarity tool is the weakest localization method tested.
5. Reported: the public leaderboard is 58 tasks, the top (0.24 = 14 tasks) is 16 teams resubmitting one
   family of single-agent 31B configurations, and the same file varies by 2-5 tasks between submissions.
6. Reported: 8-minute, 40-call bundles have exceeded the 12-hour limit on resubmission, which scores nothing.

## 17. Biggest remaining weaknesses

- No leaderboard score exists for this submission.
- 9 of 36 runs end with no edit, cause undiagnosed (`docs/FAILURE_ANALYSIS.md`).
- Multi-file and larger fixes almost always fail.
- All measurements are single runs on 36 tasks from two repositories.
- No adapter, no smaller-model entry, no verifier agent was tested.
- Rule question open: hosts have not answered whether an AI-built entry meets the "own original work"
  requirement (thread 743007).

## 18. Recommended final submission

Submit `submission.zip` as built from `submission/` (agent v3, 5 minutes, 30 calls).

- Rebuild: `python scripts/build_submission.py`
- Validate: `python scripts/validate_submission.py`
- Smoke test: `python scripts/run_smoke_test.py --data <competition data dir>`

Expected leaderboard result (Hypothesis): the same band as the public single-agent family, about 0.16-0.22,
with the exact value decided mostly by noise. Reaching the very top of the public board would need a lucky
draw; nothing measured here supports a claim of a real edge.

With one submission a day and about a day of turnaround, roughly ten scored attempts remain before the
deadline. Resubmitting the same file and selecting the two best is what the top of the public board is doing;
it improves the public score, not the private one.

## 19. Is the small-model bonus strategy justified?

Not tested here. Reported: the small-model board tops out near 0.06 with E4B. The bonus goes to the
highest-ranked E2B/E4B entry among a team's two selected submissions, so entering costs one of the two final
slots. Hypothesis: worth one slot only if the E4B entry is tuned and scored at least once first; an untested
E4B entry is not justified.

## Reproducing

- Experiments: `experiments/E01`-`E05` with per-task results; configurations in `submission/`,
  `experiments/baseline/`, `experiments/baseline_5min/`.
- Evaluation notebooks are generated by `scripts/make_eval_notebook.py` and pushed with
  `scripts/kaggle_kernel.py`.
