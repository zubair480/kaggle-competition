# v5 candidate (not submitted, not measured)

v4 (`submission/`) plus three prompt-only changes from `research/small_model_methods_2026H2.md`:

1. First reply must contain a three-line plan (NAMES / CHANGE / CHECK) together with the first tool call.
   A reply without a tool call ends the task in this harness, so the plan is never a separate turn.
2. Literal call form for the two no-argument tools (`get_status`, `submit_patch`): empty arguments.
3. After a tool error the next call must differ; a failed reproduction never cancels the edit.

Target: the quarter of runs that end with no edit (`docs/FAILURE_ANALYSIS.md`).
Status: passes official validation and the local smoke test. No model run yet (no GPU quota).
