# Competition facts

Verified on 2026-11-21 (UTC) against the live Kaggle pages, the Kaggle API and the installed harness
(`swegemma 0.2.11`, `adk-submission 0.2.13`, `adk-eval-core 0.1.0`, wheelhouse dataset v31 dated 2026-10-12).

Confidence: **High** = read directly from an official source or the harness code; **Medium** = stated by
participants with measurements, not confirmed by staff; **Low** = inference.

| # | Fact | Source | Confidence |
|---|---|---|---|
| 1 | Host: Google DeepMind. Featured competition, awards points and medals. 6,308 teams on the leaderboard. | Kaggle API `competitions/list`, leaderboard download | High |
| 2 | Final submission deadline 2026-12-02 23:59 UTC. Entry and team-merger deadline 2026-11-25 23:59 UTC. Paper deadline 2026-11-12 (passed). | Overview > Timeline; API `deadline`, `newEntrantDeadline` | High |
| 3 | Prizes: main track $65,000 (37k / 18k / 10k), paper track $35,000, small-model bonus $10,000. | Overview > Prizes | High |
| 4 | Small-model bonus: highest-ranking submission that uses Gemma E2B or E4B as base model; it must be one of the team's two selected final submissions; ranked on the private test set; LoRA allowed. | Overview; host thread 751104 | High |
| 5 | One submission per day; two final submissions may be selected; max team size 5. A team cannot submit while its previous submission is still scoring. | Rules 2; staff thread 747519 | High |
| 6 | Turnaround is about 20-24 hours per submission (8-9 h queue + ~9-10 h run + 2-2.5 h scoring). | Staff thread 760471 (2026-11-18) | High |
| 7 | Submission = `submission.zip` with `agent.yaml` at the root (declarative ADK config, prompts, optional sub-agents, skills, LoRA adapters). No Python entry point. | Overview > Evaluation; HARNESS_README s2 | High |
| 8 | Hard limit: unpacked size < 3 GiB. Allowed extensions: .yaml .yml .md .txt .py .json .safetensors. No symlinks, no `..`. | HARNESS_README s2.4; `swegemma.config` | High |
| 9 | Allowed base models: `gemma-4-{31b,12b,e4b,e2b}-it-qat-w4a16-ct`. One base model per submission; different agents may use different LoRA adapters. | Overview; HARNESS_README s3 | High |
| 10 | Scoring hardware: 4x NVIDIA L4, vLLM 0.19.1, tensor parallel 4, `max_model_len` 32,768. | HARNESS_README s3.1; wheelhouse | High |
| 11 | Metric: resolution rate. A task counts only if pytest exits 0 and every required test passed (JUnit XML check). | HARNESS_README s8.2; `harness/verification.py` | High |
| 12 | Total budget: 12 hours to produce patches for all tasks, including sandbox setup, excluding patch validation. Exceeding it fails the whole submission. | Overview > Evaluation; participants in 746250 | High (limit) / Medium (failure mode) |
| 13 | Tasks are run sequentially on the scorer; about 120 hidden tasks; a 4.5-minute cap took about 10 hours in scored runs, i.e. ~0.5 min overhead per task. | Participants in 746250 | Medium |
| 14 | The public leaderboard is computed on exactly 58 tasks, so scores move in steps of 1/58 = 0.017. | Thread 743506; consistent with the score histogram (0.24, 0.22, 0.20, 0.18, 0.17 ...) | Medium-High |
| 15 | Leaderboard on 2026-11-21: 16 teams at 0.24 (14/58), 125 at 0.22 (13/58), 595 at 0.20 (12/58), 1,219 at 0.18. | Official leaderboard download (`research/leaderboard_score_histogram.json`) | High |
| 16 | Per-task budgets come from the submission's `eval_config.yaml` (`max_time_minutes`, `max_tool_calls`, `max_turns`, `timeout_seconds`). Scorer defaults are 60 min / 100 calls / 500 turns. | HARNESS_README s7; starter notebook | High |
| 17 | If the agent never calls `submit_patch`, the harness still extracts the working-tree diff and scores it. | HARNESS_README s8.1 | High |
| 18 | Edits to test files and runner config files are stripped from the patch and reset before tests run. | HARNESS_README s8; `strip_protected_files_from_patch` | High |
| 19 | Public development set: 129 tasks (fastapi 67, rich 48, requests 13, httpx 1), with snapshots, graphs and embeddings for 127. | `tasks.jsonl`; data listing | High |
| 20 | The hidden set uses different, unseen tasks. Local resolution rates on the 129 public tasks (~35-43% in community runs) are roughly double the public leaderboard scores (max 24%). | Community runs in 746250 vs leaderboard | Medium |
| 21 | External data and models are allowed if reasonably accessible to all at minimal cost; automated ML tools are allowed with an appropriate licence. | Rules 6 | High |
| 22 | Winners must license the submission and the code that generated it under an OSI-approved licence (Apache 2.0 named). | Rules 5-6 | High |
| 23 | One Kaggle account per person; no private code sharing outside the team during the competition. | Rules (general) | High |
| 24 | Whether an entry designed, built and uploaded by an AI assistant satisfies the "own original work" requirement was asked of the hosts on 2026-11-19 (welcome thread 743007) and had no host reply when read. | Thread 743007 | High that it is unanswered |
| 25 | L4x4 notebook sessions must have internet disabled and burn GPU quota at twice the normal rate. | Overview > Upgraded Accelerators | High |

## Corrections to the starting assumptions in the brief

- "Hidden evaluation uses private repositories": the official text says private and public test *sets*; it does
  not say which repositories they come from. Treat repository identity as unknown.
- The 12-hour budget includes sandbox setup; model start-up is not itemised in the official text.
- The public set has 129 tasks, but graphs, embeddings and snapshot-derived data exist for 127 of them.
