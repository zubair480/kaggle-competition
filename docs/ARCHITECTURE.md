# Architecture

## Shape

One agent, one model, six tools, one prompt. No sub-agents, no skills, no adapters.

```
submission/
  agent.yaml              swe_agent, gemma-4-31b-it-qat-w4a16-ct, 6 tools
  prompts/system.md       budget, workflow, test contract, rules, tool tips, pinned task statement
  configs/sampling.yaml   temperature 0.2, top_p 0.95, thinking on with summaries
  eval_config.yaml        per-task time, call and turn caps
```

## Why a single agent

| Option | Decision | Evidence |
|---|---|---|
| Single 31B agent | **Used** | Every public configuration with a leaderboard badge of 0.20 or more is this shape (`research/competitor_repositories/`). |
| Sub-agents (planner, coder, reviewer) | Not used | Each hand-off costs calls and context inside a 32k window with a 5-8 minute cap. No public result shows a gain; the public multi-agent bundles sit at or below the single-agent family. |
| Smaller base model (12B, E4B, E2B) | Not used for the main entry | Reported E4B scores are about 0.05-0.06; reported 12B runs exceeded the 12-hour limit (`research/kaggle_discussion_findings.md`). |
| LoRA adapter | Not used | No GPU training budget in this project and no public evidence of a gain. Untested, not disproven. |
| Code-graph tools | Not declared | Measured weakest localization strategy, 15% empty results (`docs/RETRIEVAL_RESEARCH.md`). Not declaring them also removes their section from the harness's task prompt. |
| Best-of-N or self-consistency | Not possible | The submission is declarative; there is no orchestration code, and N runs would multiply the time budget. |

## The four constraints the prompt is built around

1. **Time is the binding constraint, not intelligence.** About 120 tasks run one after another inside 12 hours.
   The prompt therefore sets call-number deadlines (edit by call 12, no new exploration after call 20) instead
   of an open-ended "investigate thoroughly".
2. **The working tree is graded even without `submit_patch`.** So an early concrete edit dominates a late
   perfect one. The prompt says so explicitly.
3. **History compaction drops tool results** once the prompt passes 14,336 tokens. Two counter-measures:
   the task statement is pinned at the end of the system prompt through `{problem_description}`, and the agent
   is told to restate key facts (file, function, lines) in its own reply text, which survives compaction.
4. **Hidden tests check the stated contract.** The prompt has a section on what the hidden tests check: exact
   names, signatures, error types and messages; follow the closest sibling feature; fix the root cause.

## Elements borrowed from the published literature

Only the parts that fit a declarative, single-pass agent were used. See `research/literature_review.md`.

- Localize, then repair, then check (the Agentless and SWE-agent line of work): the six workflow steps.
- Narrow, line-ranged file views and filtered search output (SWE-agent's interface findings): steps 2 and 3.
- "Reason about what the tests will check before editing" (the desk-check idea in the brief): the
  "What the hidden tests check" section. A separate verifier agent was not built, for the cost reasons above.

## Sampling

Temperature 0.2, top_p 0.95, thinking enabled with thought summaries included. Public ablations report that
turning thinking off or hiding thought summaries lowers scores; this project did not re-measure that.

## Budgets

See `docs/FINAL_REPORT.md` for the final values and the measured timings they are based on.

## What is deliberately absent

- No task ids, repository names, reference patches or test names anywhere in `submission/`
  (`scripts/validate_submission.py` checks this).
- No instruction to exploit tasks that pass with an empty patch.
- No credentials and no network use.
