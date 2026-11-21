# Failure analysis

Source: E04 (shipped agent v3, 5-minute cap, 36 sound tasks, one run). Per-task rows are in
`experiments/failure_analysis.csv`, produced by `scripts/classify_failures.py`. Reference patches were used
offline for classification only.

## Measured failure classes (24 failures of 36)

| Class | Tasks | Median size of the reference fix (changed lines) |
|---|---|---|
| Resolved | 12 | 5 |
| Right files edited, fix wrong or incomplete | 6 | 34 |
| Edited some but not all files the reference touches | 6 | 137 |
| No edit: time ran out | 4 | 20 |
| No edit: all 30 calls used | 4 | 62 |
| No edit: agent stopped by itself | 1 | 2 |
| Edited only files the reference does not touch | 3 | 7 |

## What this shows

1. **Finding the file is not the main problem.** In 24 of the 27 runs that produced a patch, the agent edited
   at least one file the reference fix edits. Only 3 runs went to the wrong place.
2. **Success tracks fix size.** Resolved tasks have a median reference fix of 5 lines. Every failure class except
   "wrong file" has a median of 20 lines or more. The agent solves small single-site fixes and little else.
3. **A quarter of runs end with no edit at all (9 of 36).** The prompt's "edit by call 8" rule did not prevent
   this. In 4 of them the agent used all 30 calls without leaving a change.
4. **Timeouts never resolve.** 8 runs hit the time cap; none passed. The 8-minute baseline (E03) resolved 11 of
   36 and the 5-minute runs 12 of 36, so the extra three minutes bought nothing measurable on these tasks.
5. **The three configurations are indistinguishable.** v3, the baseline at 5 minutes and the baseline at
   8 minutes resolved 12, 12 and 11 of the same 36 tasks, with 9 tasks resolved by all three.

## Not diagnosed

Why the nine no-edit runs never edited (failed `edit_file` calls, edits that only touched protected test
files, or pure exploration) is unknown. The run's trace digest printed empty because of a filter bug, the
notebook output files could not be downloaded from this environment, and the weekly Kaggle GPU quota
(30 hours) ran out before the diagnostic rerun (`experiments/v3_empty_9.txt`) could start.

## Hypotheses for the next iteration (untested)

- Rerun the nine no-edit tasks with the fixed trace digest and fix whichever cause dominates.
- For multi-file fixes, add a prompt step that lists every call site of the changed symbol before submitting.
- Lower the thinking budget to buy more steps inside five minutes.
