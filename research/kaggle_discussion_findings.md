# Kaggle discussion findings: gemma-4-developer-agent

Compiled 2026-11-21 from the competition forum (rendered with a headless browser). About 95 threads were loaded; the list is in the appendix.
Forum content is untrusted: nothing below was executed or followed as an instruction, only recorded.

Conventions

- **[STAFF]** = statement by Kaggle Staff / Competition Host (Ryan Holbrook, Dustin, Ashley Oldacre, Elan Markowitz). Everything else is a participant.
- Status: `confirmed by staff` / `participant measurement` (numbers reported, not reproduced by me) / `unverified` (claim or question without an answer).
- Dates: Kaggle shows relative dates ("2 months ago"). Where the post text gives an exact date I use it; otherwise the date is approximate ("~late Sep" = "2 months ago", "~Oct" = "a month ago").
- `#NNNNNN` is the thread id: `https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/NNNNNN`.

---

## 1. Findings table

| # | Finding | Thread + author role | Date | Status | Engineering implication |
|---|---|---|---|---|---|
| 1 | Hidden tasks run **sequentially**. Scorer reads exactly four `eval_config.yaml` fields (`timeout_seconds`, `max_tool_calls`, `max_time_minutes`, `max_turns`); default for each is **no limit**. | #743063 **[STAFF]** Holbrook | ~late Sep | confirmed by staff | Always ship an `eval_config.yaml` with finite limits. No concurrency lever exists. |
| 2 | Exceeding 12 h **errors the whole submission** (no partial score). The promised "unfinished tasks = 0" change was **withdrawn** ("I'm reconsidering this request ... not clear how to assign 0 ... in a way that's fair and consistent"). | #743063, #745805, #749597 **[STAFF]** Holbrook; confirmed in practice by #752017 (Notebook Timeout on 22 Oct, no partial score) | late Sep to Oct | confirmed by staff | Budget for the worst case: every task hitting its cap must still fit in 12 h. |
| 3 | Public **and** private tasks (~120 total) run in the **same** 12 h run. vLLM server start-up **counts** toward the 12 h. Queue time does not. | #745805 **[STAFF]** ("Both public and private tasks are evaluated during the same 12 hour run"; "Yes" to start-up included); #747519/#760471 **[STAFF]** for queue | Oct to 18 Nov | confirmed by staff | Per-task cap ~ (12 h - start-up - margin) / ~120. |
| 4 | Patch validation is outside the 12 h: "around two hours if a patch is submitted for every task"; a task with no patch skips validation and scores 0; a "no patch" submission takes ~10 min. | #743663 **[STAFF]** Holbrook | ~late Sep | confirmed by staff | Total wall clock = agent phase (<=12 h) + ~2 h validation. |
| 5 | Public LB = exactly **58 tasks**, score truncated (not rounded); 1 task = 0.0172. | #743506 participant (derivation from observed scores); corroborated #753524 | ~late Sep | participant measurement | 0.24 = 14 tasks, 0.22 = 13, 0.20 = 12, 0.17 = 10, 0.15 = 9. |
| 6 | Same ZIP rescored varies by several tasks: 0.15/0.17/0.15; 0.22/0.17/0.15; 0.17 then 0.12; 0.20/0.18/0.17/0.17/0.17/0.13; 0.13 to 0.20; public "0.24" bundle reran at 0.17; one case 0.18 then 0.01. | #757588, #758969, #756438, #750350, #748584, #759514, #750521 participants | Oct to Nov | participant measurement | A single LB score is weak evidence; differences under ~3 tasks (0.05) are noise. |
| 7 | Private score: no multi-run averaging announced. Ties broken by earlier submission date. "Deterministic inference doesn't solve the problem of submission variance." | #760126 **[STAFF]** Holbrook; #754295 (no staff answer) | 18 Nov | confirmed by staff (ties); unverified (single run) | Pick finals for robustness; submit early when equal. |
| 8 | 0.29 top score was an exploit: "We fixed a bug in the metric that was allowing some agents to achieve improperly high scores"; rescoring finished; "The metric patch only affected exploits ... Standard agent behaviors shouldn't be affected." | #760126 **[STAFF]** Holbrook | 18-20 Nov | confirmed by staff | Real ceiling on public LB is 0.24 (14/58). Do not chase scorer loopholes. |
| 9 | Hidden test repos are **private repositories**, none of the training repos (fastapi, rich, requests, httpx) are in the test set; "every task in the test set is solvable and validates at 100% with a 'gold patch' submission". | #744951, #747248, #742882 **[STAFF]** Holbrook | late Sep to ~9 Oct | confirmed by staff | Do not overfit to the four public repos. Public gold-patch failures are a public-environment artifact. |
| 10 | Public environment is broken for many tasks: gold patch passes on 52/129 in a plain notebook (fastapi 10/67); 43/129 in the public Docker path; 127/129 in a rebuilt "scorer-like" sandbox. Missing wheels: `typing_inspection`, `inline_snapshot`, `dirty_equals`, `annotated_doc`, `pytest-httpbin`; newest-starlette vs old fastapi commits; bundled release wheels shadow `/workspace`. | #751487, #747248, #745775, #750345, #756400, #749114 participants | Oct | participant measurement | Local eval must use a repaired sandbox, or restrict to tasks where gold passes and empty fails (68 to 124 tasks depending on setup). |
| 11 | Private Docker sandbox "uses the same base image but installs a different set of dependencies because the test issues come from a different set of repos". | #742882 **[STAFF]** Holbrook | ~early Oct | confirmed by staff | Dependency shadowing on public tasks does not predict hidden behaviour. |
| 12 | Compaction on the scorer: participants report `token_threshold=14,336`, `compaction_interval=5`, overlap 2, retention 5 (README since 25 Sep + Getting Started notebook). Staff never stated the number. | #744692, #748584, #747186 participants; **[STAFF]** only "I will look into it" | Sep to Oct | unverified (consistent participant reading of README) | Assume compaction fires at ~14.3k prompt tokens, i.e. after a handful of tool calls. |
| 13 | Compaction summarizer (`LlmEventSummarizer`) keeps only `part.text`; tool calls and tool results are dropped. Submissions cannot change the summary prompt. Staff will not migrate to ADK v2. | #754783, #747186, #744794 participants; #748287 **[STAFF]** ("too risky to attempt a migration to ADK v2") | Oct to Nov | participant measurement (code read) + staff on ADK v2 | Make the agent restate key facts (file, line, test result) in visible text/thoughts before each call so they survive compaction. |
| 14 | Context overflow ends the task with an **empty patch**: `ContextWindowExceededError` goes to generic `except`, which skips the fallback `git diff` capture. 44/44 overflowed sessions had empty patch; ~12% of sessions overflowed at threshold 14,336, 17-33% at 32,768. Headroom = 32,768 - 14,336 - max_output_tokens. | #744692, #747791 participants | late Sep to Oct | participant measurement; fix status unverified | Keep `max_output_tokens` well below 16,384 (public configs use 4,096-8,192) and cap tool output sizes. |
| 15 | Calling an undeclared/hallucinated tool raises `ValueError` and ends the task with empty patch. The task message advertises graph tools regardless of what `agent.yaml` declares. Staff: "A fix for bad tool calls will also be live soon." | #745028 participant; #745805 **[STAFF]** | late Sep to Oct | reported; fix promised by staff, not confirmed live | Safer to declare the graph tools (even if discouraged in prompt) than to omit them. |
| 16 | Tool results were double-JSON-encoded; fixed in the **30 Sep** wheelhouse: now one level of JSON, and `edit_file` retries with escapes removed. Residual: repair is tied to `old_string`; an escaped `new_string` is written verbatim when `old_string` matched exactly. | #744272 **[STAFF]** ("The latest wheelhouse should have this fixed") + participants | 30 Sep; residual 8 Nov | confirmed by staff; residual is participant measurement | Model sees `\n`, `\"` in read_file output. Tell it to write real characters in `new_string`. |
| 17 | `edit_file`/`write_file` calls lose arguments in vLLM 0.19.1's gemma4 parser (string closed with a backtick, `"""` docstrings): ADK rejects with "mandatory input parameters are not present". Rates: 60/234 edit_file and 20/255 write_file vs 0/1,135 run_command; 105/524 in Budget-Fit; 107/246 (43%). Model resends identical call (up to 34 times). Rejected calls do not count toward the tool-call cap but cost time. | #747519 (Syurolh), #748323, #747923, #747168 participants | Oct | participant measurement; not fixed | Prompt: never resend a rejected call; avoid docstrings/backticks in `old_string`; offer a single-string-argument edit path via `run_command`. |
| 18 | gemma4 tool parser can **loop forever** on array-valued arguments containing `]` (e.g. `args:["Fix list[str] handling"]`), freezing the inference server for all later tasks. Upstream fix vllm #41991 shipped in v0.21.0; scorer pins 0.19.1. No staff answer. | #753973, #745138, #746336 participants | Oct to Nov | participant measurement; not fixed | Avoid tools with array arguments (`run_skill_script` `args`). This is the main argument against skills with scripts. |
| 19 | Thoughts between tool calls were dropped (vLLM reads `reasoning`, ADK sent `reasoning_content`). Staff: "unambiguously a bug. The fix should be in the current wheelhouse." Fix is client-side in `adk_submission` >= 0.2.12 (30 Sep). | #744354 **[STAFF]** Holbrook; mechanism from participant code read | 30 Sep | confirmed by staff | Thoughts now persist and consume context; compaction triggers earlier than in pre-30-Sep traces. |
| 20 | `include_thoughts: false` no longer disables thinking since adk_submission 0.2.13 (8 Oct, wheelhouse v29/v30): default budget 4096 applies. Only `thinking_budget: 0` turns thinking off. Staff: "This was intended." | #747914 **[STAFF]** Holbrook | ~10 Oct | confirmed by staff | Set `thinking_budget` explicitly. `include_thoughts` only controls whether thoughts are carried in history. |
| 21 | `thinking_budget` and `seed` were not forwarded (v25); fixed ("The most recent wheelhouse dataset should have the patches"); participant verified on v28 that both reach vLLM. | #744566 **[STAFF]** + participant | late Sep; re-test ~3 Nov | confirmed by staff | Budgets are honoured now. |
| 22 | LoRA on scorer: (a) double layer registration wiped adapters, fixed in wheelhouse **v23**; (b) KV cache shrank to 7,600 tokens with fixed `max_loras=8, max_lora_rank=128`, fixed: "vLLM will set its LoRA params dynamically based on what you actually submit"; (c) adapters are applied correctly and "the scoring environment uses the exact same patched vLLM 0.19.1 wheelhouse". | #743508, #744331, #744794, #749528 **[STAFF]** Holbrook | late Sep to mid Oct | confirmed by staff | LoRA works mechanically. Use one adapter with the lowest rank that works. |
| 23 | LoRA still costs: KV cache 36,432 -> 27,712 tokens with one rank-16 adapter (v28, util 0.80); decode 10-25% slower; zero-B adapter resolved 50/129 vs base 57/129. | #744331 (Baume), #760309, #749191, #751596 participants | Oct to Nov | participant measurement | An adapter must gain ~5 pp just to break even at a fixed time cap. |
| 24 | Nobody on the forum reports a reproducible LoRA gain; SFT/distillation adapters tie or lose to base (31B and E4B). Scale `alpha/r = 2` produced degenerate loops in one report; `alpha/r = 1` fixed it. | #751596, #750713, #750961, #753793, #760014, #748051 participants | Oct to Nov | participant measurement | Prompt/config-only is the lower-risk path at this point. |
| 25 | Model variants: one variant per submission ("Every agent and subagent in your submission must use the same variant"). Smaller variants scored under identical conditions ("Yes, everything is the same"). 12B needs `--hf-overrides`; "The scorer has this update already". | #748287 **[STAFF]** Holbrook | ~Oct | confirmed by staff | A stray second `agent.yaml` with another model in the zip causes "Notebook Threw Exception" (#758969). |
| 26 | 31B beats 12B and E4B with the same agent files: 9 and 11 /31 (31B) vs 4/31 (12B) vs 0/31 (E4B). On 4xL4: 31B 33-35 tok/s, 12B 62-64 tok/s, but 12B emits 1.8x more tokens per call. | #750974 participants | ~Oct | participant measurement | Use 31B for the main prize. |
| 27 | Small Model Prize: $10,000 for the highest-ranking submission using E2B or E4B; must be one of the team's two final selections; best small-model score reported 0.06 (20 Oct). Deadline 2 Dec per participant reading; staff did not answer. | #751104 **[HOST]** Markowitz; #757244 participants | ~Oct; 9 Nov | confirmed by host (prize); unverified (deadline wording) | Using a final slot on E4B sacrifices main-track robustness. |
| 28 | Thinking helps 31B: thinking off 23/129 vs 48/129; hiding thought summaries 35/129 vs 51/129. For E4B it is the opposite: think=4096 10/114 vs zero-think 16/114. | #746250, #760014 participants | Oct to Nov | participant measurement | 31B: `thinking_budget` 2048-4096, `include_thoughts: true`. |
| 29 | Kaggle 4xL4 speed: 900.8 s per 1M model tokens (1,110 total tok/s), 8.68 s per model call with thinking; a 4.5-min cap took ~10 h total (so ~0.5 min/task overhead); 5.5 min/task is the commonly used safe cap; 8-min caps time out. | #746250, #747857, #748168 participants | Oct | participant measurement | Cap 4.5-5.5 min with 24-32 tool calls is the proven-to-finish region. |
| 30 | Graph tools: `search_similar_code` is an exact node-name lookup (not text search); returned results for 82 -> 11 -> 270 -> 270 of the same 314 calls across the pre-30-Sep / 30 Sep / 8 Oct / 9 Oct builds. No measured solve-rate benefit (34/68 without vs 32/68 with; 55 vs 50 /129). | #748323, #745220, #744040, #746250, #756400 participants | Oct to Nov | participant measurement | Graph tools are optional; if used, pass full dotted node names. |
| 31 | Async functions are missing from all code graphs; host: private tasks do not touch any `async def` function, and async is "at most 1.8% of functions" in private repos; graphs will not be regenerated. | #745998 **[HOST]** Markowitz | ~late Sep | confirmed by host | Not a hidden-set concern. Also tells us private repos are mostly synchronous Python. |
| 32 | External-LLM distillation: "As long as you are using those models in accordance with their model license terms, and the output you're using ... doesn't conflict with the license requirement of the rules of this competition, you may use them." | #742807 **[STAFF]** Oldacre (pinned) | ~late Sep | confirmed by staff | Allowed in principle; teacher's ToS is the participant's responsibility. |
| 33 | Private sharing of code/data outside the team is not permitted; sharing must be public via forums/notebooks. | #742815 **[STAFF]** Oldacre | ~late Sep | confirmed by staff | Reusing public Apache-2.0 notebooks is fine; private exchange is not. |
| 34 | Eligibility of an entry "designed, built, tested, and uploaded" by an AI assistant: asked 19 Nov, **no staff answer**. | #743007 participant (Itachi45) | 19 Nov | unverified | Open risk; rely on the rules text, not the forum. |
| 35 | Queue: ~8-9 h in queue + run; "~94% complete end-to-end in under 24 hours"; one pending submission per team (separate from 1/day). | #760471, #747519 **[STAFF]** | 18 Nov | confirmed by staff | With the 2 Dec deadline, roughly one scored attempt per day at best; a stuck run blocks the team. |
| 36 | Zip packaging: archives with directory entries fail within an hour with no explanation; use `zip -D -X -r ../submission.zip .` | #752282 participant | ~Oct | participant measurement (2 lost submissions) | Build the zip with `-D`. |
| 37 | `eval_config.yaml` with explicit `null` budgets may crash the scorer entry point (`int(None)` in the Getting Started budget block). | #760140 participant | 18 Nov | unverified (local reproduction of the notebook block only) | Use finite numbers, never `null`. |
| 38 | Verification runs only the tests selected by `test_patch`; a patch that regresses 2 other tests still got `resolved=True` locally. | #750175 participant; no staff answer | ~Oct | participant measurement | Do not spend budget running the whole suite. |
| 39 | Test-file reset before `test_patch` was a no-op (edited test files made `test_patch` fail to apply). Staff: "The test-file reset fix will be live soon"; the 8 Oct build "drops edits to test files from the submitted patch". | #744825 **[STAFF]** ("Addressing now"); #745805 **[STAFF]**; #748323 participant (wheel diff) | late Sep to 8 Oct | confirmed by staff (fix), build date from participant | Still tell the agent not to edit existing tests. |
| 40 | Stronger models barely beat 31B in this harness: DeepSeek V4 Pro 58/124, Qwen3.6-27B 59/123 vs Gemma 31B 54/124 and 53/123; 15% of tasks flip between two identical Gemma passes. | #747168 participant | ~Oct | participant measurement | The harness (32k context, compaction, budget, sparse task text) is the bottleneck; distillation has little headroom. |

---

## 2. Scorer and budget facts

**[STAFF] statements**

- Sequential execution; four `eval_config.yaml` fields only; "The default is no limit." (#743063)
- "Currently, hitting the 12-hour limit will error ... You may want to set max_time_minutes to something moderate as a failsafe." Later: "I'm reconsidering this request. The trouble is that we run both the public and the private tasks during the same 12 hour evaluation" (#743063, #745805). On #749597: "Naively setting unfinished tasks to 0 could lead to inconsistent results on the public and private leaderboards."
- 12 h includes vLLM start-up ("Yes", #745805 item 6). Queue time is not charged (#747519).
- Patch validation: "around two hours if a patch is submitted for every task"; no patch means validation skipped and score 0 (#743663).
- "Patch verification generally shouldn't timeout" (answer to whether `timeout_seconds` applies to the hidden verification run; "I will double check this and fix if necessary", #745805). A participant wheel diff says the 12 Oct build gave the test run "its own 300 s limit" (#748323).
- "I didn't observe any significant command overhead compared to a plain container." (#745805)
- Per-submission aggregate diagnostics (timeouts, overflow counts): "Probably not. Information like this makes it too easy to extract information about the test set through probing." (#745805)
- Hidden repos are private and disjoint from the training repos; gold patches validate at 100% (#744951, #747248, #742882).
- Ties: "ties are resolved by submission date. Earlier submissions win." (#760126)
- Metric exploit patched and rescored; standard agents unaffected (#760126).
- Queue (18 Nov): "~8-9 hours in the queue before starting execution, followed by ~2-2.5 hours for scoring"; average notebook runtime "~9-10 hours per submission"; ~94% complete in under 24 h (#760471). Pending-submission limit of one per team (#747519). "It's possible, yes, that you will lose a daily submission this way." (#747519, Holbrook)
- Failure waves acknowledged as host-side: GPU outage night of 30 Sep/1 Oct (#744807); "This looks like a failure on our side" for the ~21 Oct "Notebook Threw Exception" wave (#751339); queue-timeout "Kaggle Error" for runs waiting >15 h, since fixed (#747519).

**Participant measurements**

- Public LB = 58 tasks, truncated display (#743506). About 120 tasks in the run; the data page says "about 120 ... evenly divided".
- Kaggle 4xL4, 31B, TP=4, sequential: 5.55M model tokens in 5,002 s of LLM time = 900.8 s/M tokens, 1,110 tok/s total, 8.68 s per model call with thinking on (#746250). 3.8 s per call with thinking off (#746250 comment, Zhukov).
- "In our scored runs, a 4.5-minute cap took about 10 hours, so each task adds roughly 0.5 minutes of setup and verification on top of the cap." (#746250, Zhukov)
- Operating point used by several teams: `max_time_minutes` 5.5 (120 x 5.5 = 11 h) (#746250, #747857). A 5.5-min Kaggle submission completed (#747857). "5.5 mins ... gives you a trajectory of 40-50 llm and tool calls spanning 300-350k tokens" (#746250).
- Reported finish/timeout outcomes on the LB (#748168, #750350, #748287, #756400, #750974): 4 min/60 calls scored; 5 min/24 calls 0.13; 5 min/28 calls 0.15; 8 min/32 calls timed out; 8 min/28 calls timed out (one author) while Budget-Fit style 8 min/28 calls bundles score for others (cap is rarely reached because the 28-call cap binds first); 7 min/28 calls timed out for a sequential-agent setup; 10 min/60 calls timed out; 15 min timed out; 12B with 8 min timed out.
- vLLM start-up on 4xL4: ~340 s (#744807), 454-743 s on 20 Oct, 514-1,677 s on 21 Oct with 3 of 7 starts over the 1,200 s health limit (#747519 Syurolh, #751264). Observed fixed notebook/vLLM setup 12.6 min (#746250).
- Adding a verification step (re-running the whole touched test file) looked like +5% median time locally and produced Notebook Timeout on the hidden set (#752017): "local timing seems to under-estimate the cost of test-running steps on the hidden repos".
- Budget warning text from the harness ("Only N tool call(s) remaining ... Finalize your edits") starts when 10 calls remain, for caps >= 20. Nothing warns about time (#749198). `get_status` exists for remaining budget (#749597).
- `run_command` is synchronous and blocks the event loop (#747168); irrelevant on the scorer (sequential) but matters for local parallel eval: run one task per process.
- One clock, one call counter, one turn counter for the whole task (`EvaluationBudget`); no per-agent limits; `exit_loop` is not in the tool registry (#747519 Syurolh).
- Initial task prompt "Workspace Layout" is `find -maxdepth 3 | sort | head -150`; in 115/129 public tasks the package directory is cut off (#745220). The 8 Oct build "prunes the repository listing in the first prompt" (#748323).
- `read_file` truncates at 150 lines (#755291). Tool output cap 5,000 characters (#748323, #760595).
- `write_file("/tmp/x.py")` strips the leading slash and writes to `/workspace/tmp/x.py`, which lands in the patch (#760595).
- `pytest ... | tail -15` returns tail's exit code, so the tool reports `"status": "ok"` on failing tests (#760595).

---

## 3. Harness bugs and fixes by wheelhouse date

Staff never published a changelog; version/date mapping below comes from participant wheel diffs (#748323, #744354 comments) plus staff "fixed in latest wheelhouse" replies.

| Date / version | Change | Source |
|---|---|---|
| 25 Sep (first wheelhouse; swegemma 0.2.7, adk-submission 0.2.11, google-adk 1.36.1, vLLM 0.19.1 patched) | Released by staff. Sample submission (with adapters) failed on the scorer; scored 0.01 without the failure for another user. | #742882 **[STAFF]**, #743213, #743140 |
| v23 (late Sep) | LoRA zeroing bug (decoder layers registered twice) fixed: "The zeroing fix landed in v23 of the wheelhouse dataset (now on v25)". | #743508 **[STAFF]** |
| 30 Sep (adk-submission 0.2.12; swegemma still 0.2.7 but 10 files changed) | Tool results single JSON level + `edit_file` unescape fallback; `reasoning_content` mirrored to `reasoning`; `thinking_budget`/`seed` forwarded; vLLM started with `--reasoning-config` and `--no-scheduler-reserve-full-isl`; LoRA params sized from the submission. Graph tools regressed (11/314 calls returned results). | #744272, #744354, #744566, #744794 **[STAFF]**; #744807, #748323 participants |
| 8 Oct (swegemma 0.2.10, adk-submission 0.2.13; wheelhouse v29/v30) | Graph tools answer again (270/314); edits to test files dropped from the submitted patch; repository listing pruned in first prompt; `include_thoughts: false` no longer disables thinking (staff: intended). | #748323 participant; #747914 **[STAFF]** |
| 9 Oct (swegemma 0.2.11) | `swegemma/models/discovery.py` and `models/registry.py` removed (old starter notebook import breaks). | #748323 participant |
| 12 Oct 19:51 UTC (0.2.11 repackaged, wheelhouse v31) | budget, cli, config, context, harness/verification changed; "the test run now has its own 300 s limit". 12B weight-loading (`vision_embedder.*`) fixed "in the most recent wheelhouse". Wheelhouse reported unchanged from 12 Oct through at least 11 Nov. | #748323 participant; #748287 **[STAFF]**; #744354 participant |
| Wheels are cp312 | Wheelhouse works on Python 3.12.13 (notebook environment pinned 2026-07-01); nine wheels fail on Python 3.13. | #748287 participant |

Open / unfixed as far as the forum shows

- gemma4 tool-parser infinite loop on array arguments (#753973, #745138, #746336). No staff reply.
- Argument loss on long string arguments ("mandatory input parameters are not present") (#747519, #748323).
- Plain JSON quotes in a tool call keep the quote characters in the value (`skill_name:"my-skill"` arrives as `"\"my-skill\""`) (#746336 comment).
- Compaction summarizer drops tool calls/results (#754783); staff "I'll look into the compaction issue" (#744794), no follow-up.
- Context overflow discards the patch (#744692); staff "I will look into it", no follow-up.
- `run_skill_script` with `file_path` as a list raises `AttributeError` and ends the task with an empty patch, ~3% of task-runs (33 of 960), always on the first skill call or first after compaction (#745028 comment).
- ADK 1.36 ParallelAgent with tool calls is broken (upstream adk-python #7324); staff will not migrate; workaround is tool-free sub-agents (#748287).
- Chat template is the original June template, not the 15 Jul refresh; staff "I will investigate!" (#744844).
- Missing test wheels in the public `wheels/` (124 wheels) (#747519 Syurolh, #745775).
- Skills submission scoring 0.00 with no error for some teams, working for others (#750350, #750887).

---

## 4. LoRA serving

**[STAFF]**

- Adapters are served as named vLLM LoRA modules; `discover_adapters` expects the submission root (#743508).
- "Now vLLM will set its LoRA params dynamically based on what you actually submit. Submitting fewer adapters with lower rank (or no adapters) leaves more memory for KV-cache." (#744794)
- "the adapters are being applied correctly ... the scoring environment uses the exact same patched vLLM 0.19.1 wheelhouse"; the sample adapter only touches layer 0 `q_proj`/`o_proj`, and Gemma 4's RMSNorm placement damps it, which is why noise there barely moves logits (#749528).
- LoRA base weights for training: "The unquantized variants are on the same page" (#748287).
- Different agents may attach different adapters, same base variant (#748287).

**Participant measurements**

- Before the fix (v25, `--max-loras 8 --max-lora-rank 128`, util 0.90): KV cache 46,048 tokens without adapters, 7,600 with; prompts over ~7.6k hung (#744331).
- After (v28, util 0.80, one rank-16 adapter): 36,432 -> 27,712 tokens (0.76x); 28k prompts complete. With `cudagraph_specialize_lora: False` it would keep 34,288, but submissions cannot set it (#744331).
- Two adapters rank 4 (`max_loras=2, max_lora_rank=8`): 6.06 GiB/GPU for the model, KV cache 27,696 tokens (#743508).
- Scorer values quoted by participants: `gpu_memory_utilization=0.80`, `max_model_len=32768`, TP=4 (#743508, #744331). Not stated by staff.
- Start-up OOM "when warming up sampler with 256 dummy requests" with one rank-16 adapter at util 0.8, reproduced 3 times (#749191); no staff answer. Same adapter shape scored once (19 Oct) and errored once (21 Oct, during the infrastructure wave) (#749191 comment).
- Speed cost: -11% decode (#749191), -10-15% TPS on 4xL4 (#760309 comment), 15-20% more time per call (#751596), 22-25% lower TPS on A100 (#760309).
- Zero-B adapter vs base, same config, 129 tasks: 50 vs 57 resolved (single run) (#760309).
- Zero-weight adapter in the public notebook scored 0.15 five times in a row (#759514); another user got 0.13-0.20 with the same notebook.
- r=16, alpha=32 adapter and its rank-4 SVD both scored 0.00 while the same bundle without adapter scored 0.18 (#755677); another participant got a non-zero score with a rank-32 adapter and a 4-minute cap (#755677 comment).
- PEFT cannot attach to the packaged `-ct` checkpoint (`Gemma4ClippableLinear`); people train on a dequantized bf16 copy (#750713, #755677).
- Alpha is applied at inference from `adapter_config.json`: alpha 32/r 16 gave repetition loops and a 0.0 score; alpha 16 removed loops; alpha 8 was fastest (median 163 s vs 290 s) (#750713).

Training outcomes reported (all participant)

- 31B, 98 held-out tasks, prompt-only baseline solves 38: adapters solved 31, 37, 31 (#751596). LB: prompt-only 0.15-0.17, adapter 0.12.
- E4B: pure base beat multi-LoRA 14-15 vs 12.9 /114; SFT 4/20 -> 3/20, DPO 1/20 (#760014).
- E4B SFT r16/alpha32 on 170 trajectories: base 2/4 and 1/8, best SFT 1/4 and 1/8 (#750961).
- "I've gotten Lora's to work on submissions. They just scored worse than baseline." (#748051)
- A training-free SVD-derived adapter is claimed "worth about 3 tasks" on a small-model submission (#759848); another team's single run with a similar copy-fix adapter saw no change (0.06 vs 0.06) (#760595). Host ruling on hand-constructed adapters requested, not given (#756792, #759848).

---

## 5. Tool behaviour

**edit_file / write_file**

- Since 30 Sep: exact match first, then an "unescaped" fallback. `apply_replacement('x = foo("a")\n', 'foo(\"a\")', 'foo(\"b\")')` -> strategy `unescaped`. If `old_string` matches exactly but `new_string` carries escapes, they are written into the file (#744272, 8 Nov comment, swegemma 0.2.11).
- Controlled replay of 30 edit contexts at temperature 0.2: failed edits 22% with double JSON, 62% with one JSON level, 0% with raw text (#744272). The fallback rescues the copied-escape cases; what remains is argument loss: 7 of 40 edit calls with one JSON level (#744272).
- Argument-loss rates: see table row 17. Typical received arguments: `{"filepath": "reproduce_issue.py", "new_string": "...\n`,old_string:", "# Python 3.10+ union syntax": "list[str"}` (#747519).
- The harness drops test-file edits from the submitted patch since 8 Oct (#748323).
- A `run_command`-based SEARCH/REPLACE editor skill (robust-edit) cut edit failures (43% -> 29% for remaining edit_file calls, 11% for the editor) but resolved count was unchanged: 6/16 in every run (#747923). Skill scripts must not hard-code `/workspace` (subprocess sandbox uses a temp dir) (#747923).

**Graph tools**

- Graphs have only `calls` edges, no module nodes, no async functions (0 of 305) (#742911). Embeddings keyed exactly by graph node ids (#742911 comment).
- 129 of 256 graph files and 129 of 256 embedding files were empty in the public data; staff: "The embeddings are no longer empty; that has been fixed" (#742911 **[STAFF]**). Tools are enabled only when files exceed 100 bytes (README, quoted in #742911).
- `search_similar_code` = exact dictionary lookup on full dotted node name; `requests.models.RequestEncodingMixin.path_url` returns 5, `path_url` returns 0 (#745220). `get_code_neighbors` likewise; edge type is lowercase `calls`.
- Embeddings near-collapsed: mean random-pair cosine 0.78 (fastapi) to 0.90 (rich); gold file in top 10 for 35/129 vs 67 for grep (#744040).
- Usage/benefit: graph tools used on 21 of 129 tasks, all 21 semantic searches empty (#746250, pre-8-Oct build); 142 `search_similar_code` calls, 140 empty (#745028 comment, 30 Sep build); after 8 Oct, 270/314 recorded calls return results, median response 5,763 characters (#748323).
- Solve-rate effect: 50/129 with vs 55/129 without (#746250, noisy control); 32/68 with vs 34/68 without, McNemar p = 0.69; nudging use gave 14/32 (#756400). One counter-example on the LB: removing the analyzer's three graph tools went 0.13 -> 0.08 (single submissions, #747696).
- Model-free study: seeding from exact symbol names and expanding with `get_code_neighbors` put the edit site within 2 hops for 47.9% of tasks vs 14.5% Hit@5 for TF-IDF (#746250 comment).

**read_file / run_command / localization**

- `read_file` 150-line cap; one 754-line file was read 6 times and never fully seen (#755291, 12B traces).
- Command timeouts rarely bind: 0.06-0.47% of commands (#747857). `timeout_seconds` 100/150/250/300 gave 43/44/40/47 of 129 (noise).
- Localization is mostly solved by grep: gold file read by call 2 in 63% of runs and by call 3 in 76% (1,254 runs, #751596 comment); first identifier-grep hit right 30%, grep+BM25 top-5 61%, top-10 74% (#746250 comment). 35 of 128 issues contain no code identifier.
- Failure breakdown for a 31B prompt-only agent (41 failed runs): 18 edited within 20 lines of gold but wrong, 11 opened gold file and never edited, 7 edited other files only, 3 edited gold file far from change, 2 never found the file (#751596).
- Default prompt: 27 of 71 tasks never changed a source file (0 solved). Asking for a source edit by the 12th call reduced no-edit tasks 25 -> 7 on 69 shared tasks, but solves rose only 26 -> 30 (#749198).
- Solve rate 53% when the first edit comes within 3 calls after opening the right file vs 24% when it takes 12 or more (#751596 comment; correlation).

---

## 6. Model variant comparisons (numbers as reported)

| Setup | Result | Source |
|---|---|---|
| 31B, 8-min cap, Budget-Fit files, 31 unseen-repo tasks, A100 | 9 and 11 /31; 5.4 min avg; 81-84% submitted a patch | #750974 |
| 12B, 8-min cap | 4/31; 6.2 min; 42% | #750974 |
| 12B, 5-min cap | 4 and 4 /31; 4.5 min; 26% | #750974 |
| 12B, 5-min, more tool calls + thinking | 4/31; 16% | #750974 |
| 12B coder + 12B reviewer, 5-min | 3/31; 3% | #750974 |
| E4B, 5-min cap | 0/31; 1.8 min; 97% | #750974 |
| 31B vs 12B on 4xL4, 24 tasks x runs (7 min; 28 vs 22 calls) | 31B 15-21 of 48 runs (31-44%); 12B 8 of 48 (17%); 12B never solved a task 31B did not | #750974 comment |
| 4xL4 decode | 31B 33-35 tok/s; 12B 62-64 tok/s (67 tok/s single-sequence in #748287) | #750974, #748287 |
| Latency fit | 31B 1.4 s + 28.7 ms/output token; 12B 1.6 s + 16.3 ms/output token | #750974 comment |
| Output tokens per call (median) | 31B 127; 12B 233 | #750974 comment |
| Seconds per task (mean) | 31B 296; 12B 275 | #750974 comment |
| Non-empty patch | 31B 78%; 12B 46% | #750974 comment |
| 12B on the LB with 8-min cap | did not finish in 12 h | #750974 |
| 12B decode in one trace audit | 17.25 tok/s, `dt = 0.78 + 0.058*ct` | #755291 (single setup, differs from the above) |
| E2B zero-think, 114 tasks | 5 (4.4%) | #760014 |
| E4B think=4096 | 10/114 (8.8%) | #760014 |
| E4B zero-think | 16/114 (14.0%) | #760014 |
| E4B best custom system | 15/114; 10-run mean 12.90, SD 1.52; Pass@5 26/114 | #760014 |
| E4B on public LB | 0.01-0.08 band; identical reruns 0.06 and 0.03 | #758969, #760595 |
| Best small-model LB score | 0.06 on 20 Oct | #750974 comment |
| 31B full precision via OpenRouter, 28-call cap, 129 tasks | 47/129 | #758218 |
| Teachers through the same harness (25 min / 50 calls) | DeepSeek V4 Pro 58/124; Qwen3.6-27B 59/123; Gemma 31B 54/124 and 53/123; union of 4 runs 73/123; 48 solved by nobody | #747168 |

---

## 7. Rules clarifications

- **External LLM distillation** **[STAFF]** (#742807, pinned, Ashley Oldacre): "As long as you are using those models in accordance with their model license terms, and the output you're using to submit to that competition doesn't conflict with the license requirement of the rules of this competition, you may use them." No list of acceptable teachers was given. Participants disagree on whether Claude/GPT terms permit it (#749585, no staff answer). Open-weight teachers (DeepSeek, Qwen, GLM, Kimi) are what people report using.
- **Sending Competition Data to hosted APIs** (rules section 4): asked in #755542 and #742807 comments; **no staff answer**. A participant opinion ("You should be free to do whatever you like with the public data") is not a ruling.
- **AI assistance / original work**: #743007 comment (19 Nov) asks whether an entry designed, built, tested and uploaded by an AI assistant with no hands-on development is prize-eligible, and what attribution an adapted Apache-2.0 notebook needs. **No staff answer.**
- **Private sharing** **[STAFF]** (#742815): "private sharing of competition code or data outside of your team is, as always, not permitted. Code sharing must always be done publicly through the Kaggle forums/notebooks."
- **One model variant per submission** **[STAFF]** (#748287, #745805): no 31B main agent with a 12B sub-agent.
- **Small Model Prize** **[HOST]** (#751104): $10,000, E2B or E4B base, must be one of the two selected finals, LoRA allowed, also eligible for main awards.
- **Deadlines**: final submission deadline 2 Dec 2026 per participants (#744354, #757244); 12 Nov is the paper-track deadline; a question about extending it is unanswered (#760471 comments). A "25 Nov" team-merger deadline is mentioned by a participant (#748584).
- **Hand-constructed adapters** (#756792, #759848): no ruling.
- **Python startup hooks / pytest plugins in the sandbox** (#760650): asked 20 Nov, no answer.

---

## 8. What reportedly improves score, and what does not

Improves (participant measurements unless marked)

- Thinking on with summaries kept (31B): 48 -> 23 /129 when disabled; 51 -> 35 when summaries hidden. Thinking budget 2,048 vs 4,096 vs 6,144: 50 / 48 / 48 (#746250). Public 0.15-0.24 configs use `thinking_budget: 4096, include_thoughts: true`.
- Enough tool calls: 50 calls 50/129 vs 25 calls 36/129 at a 15-min local cap (#746250). On the LB, 24 calls/5 min 0.13 -> 28 calls/5 min 0.15 (single runs, #748168).
- Time cap near the Kaggle limit: local 6 min 37, 10 min 46, 15 min 54, 20 min 49, 60 min 51 of 129 on faster GPUs (#746250); at Kaggle-equivalent pace 4 min 43, 4.5 min 47, 7 min 43 of 129 (#747857, noise-level).
- A finalization/patch-hygiene instruction in the system prompt: test-patch conflicts 2 vs 8-11 with an empty prompt; pass rate 44 vs 43 at 150 s timeout but 43/40 vs 35/35 at 100/250 s (#747857).
- Temperature 0.4 or 1.0 vs 0.2: 51 vs 48 /129 (within noise) (#746250); temp 1.0 + top-k 64 gave 17/31, 17/31 vs 13/31, 13/31 (#747696).
- Mechanical self-checks after each edit (`py_compile` + import, one related test file) on E4B: 11 vs 8 of 91 locally, broken edits 12 -> 7; LB unchanged within noise (#760595).
- An explicit early-edit deadline reduces no-edit tasks (38% -> 11.6%) with a small solve gain (26 -> 30 on 69 tasks) (#749198).
- Simple single-agent prompt-only bundles hold the public 0.17-0.24 range (Budget-Fit, Budget-Aware v2, SuperAgent) (#748051, #750496, #757588).

Does not improve / hurts

- LoRA/SFT/distillation adapters: tie or lose (section 4).
- Sub-agents/analyzer: +1 task (51 vs 50) with higher runtime (#746250); "0.18 score did not come from subagents or skills" (#748051); a sequential agent with skills scored 0.03-0.08 vs 0.18 for the plain agent (#750350); second 12B reviewer 3/31 vs 4/31 (#750974).
- Graph tools: no measured gain (section 5).
- Smaller model for speed: 12B is not faster per task and solves less than half (#750974).
- Larger budgets on the LB: "40 calls / 5.5 min: 0.15, so no gain from more calls" (#758969); 154-run replay of a cap raise was null (net -1) (#753524 comment); longer caps risk the 12 h timeout.
- Forcing the agent to write a failing reproduction first (E4B): 6.0 -> 3.5 on a dev subset (#760014). "No submit in the first 3 minutes" (E4B): 0.01 (#758969).
- Prompt-level budget instructions are ignored in 61.4% of tasks (E4B) (#760014); "Prompt rules to edit earlier were mostly ignored" (#752848 comment).
- Critic/verification gates using existing tests: in ~65.7% of dev tasks the pre-existing suite already passes on unmodified code, and in ~34.3% old tests assert the buggy behaviour; 72-84% of critic "ready" verdicts were false positives (#760014).
- Cutting `max_output_tokens` 4096 -> 2560 doubled file-edit errors (53 -> 121) on E4B (#760014).
- Local CV does not rank LB scores: CV 0.316 -> LB 0.03, CV 0.211 -> LB 0.10 (#744319); two configs tied 28/74 locally scored 0.17 and 0.10 (#751973); a 50% public-set agent scored 0.05 with a 5-min cap and thinking off (#756400).
- Robust edit skill: fewer failed calls, same resolved count (#747923).

Structural limits

- 6 of 129 public tasks need names that appear nowhere in the task or repo (16 by a looser count) (#745855). 18-20 of 129 statements are only a title plus a URL; `hints_text` is empty for all 129; sandbox has no network (#746944). Staff did not say whether hidden tasks are the same.
- 35 of 38 multi-file gold patches in the practice set were never solved by any config (#753524 comment); 32.9% of dev tasks need multi-file edits (#760014).
- Tests accept some wrong fixes: 24 of 163 planted bugs (14.7%) still marked resolved (#756400).

---

## 9. Open risks

1. **Time-out = zero.** No partial scoring; hidden repos may have slower tests/commands than public ones (#752017). vLLM start-up varies from ~6 to ~28 min and counts toward the limit.
2. **Inference-server freeze** from the array-argument parser loop: one malformed call zeroes all later tasks (#753973). No fix announced. A same-ZIP 0.18 -> 0.01 report fits this (#750521 comment, cause unconfirmed).
3. **Run-to-run variance** of 2-5 tasks on 58; private split is the same size, so shake-up is expected; no multi-run averaging.
4. **Compaction at ~14.3k tokens with a summarizer blind to tool calls/results**, and context overflow that discards the patch. Scorer values never confirmed by staff.
5. **Queue and infrastructure**: ~20-24 h turnaround, one pending submission per team, stuck batches (9 Nov cohort pending 5+ days) and failure waves that consume the daily slot. Few scored attempts remain before 2 Dec.
6. **Unanswered rules questions**: AI-built entry eligibility (#743007), sending competition data to hosted APIs (#755542), hand-constructed adapters (#756792/#759848), startup hooks (#760650).
7. **Scorer/wheelhouse parity** is asserted by staff for vLLM (#749528) but there is no changelog; behaviour changed silently on 30 Sep, 8 Oct, 9 Oct, 12 Oct. Check the attached wheelhouse by file checksum, not version (#748323).
8. **Public-task evaluation is unreliable** unless the sandbox is repaired; and the hidden repos are different, mostly synchronous Python, private.
9. **LoRA path**: start-up OOM reports, slower decode, smaller KV cache, no reported net gain.
10. **Packaging pitfalls**: zip directory entries (#752282), stray extra `agent.yaml` with another model (#758969), `null` budget values (#760140), omitted `eval_config.yaml` meaning no limits (#743063).

---

## Appendix: threads loaded

Read in full or near-full: 743007, 744331, 744272, 751104, 746250, 747168, 747519 (first ~20 KB of 154 comments), 760471, 760126, 751487, 750974, 743506, 742807, 745748, 745998, 742815, 748287, 744807, 744354, 752848, 744319, 743140, 754295, 760014 (first 7 KB), 748051, 742911, 747857 (first 7 KB), 753973, 743063 (with hidden replies expanded), 745855, 750961, 747696 (first 6.5 KB), 745775, 750713 (main findings), 751596, 759514, 757588, 755677, 743508, 753524, 753793, 748323, 754783, 760309, 752017, 744692, 748584, 745028, 749597, 744794, 751264, 748443, 746169, 752282, 746008, 745805, 743663, 744825, 750175, 750350, 750887, 749528, 745059, 744566, 750496, 747923, 748168, 747186, 756438, 757626, 752671, 751986, 743213, 749198, 749114, 752511, 755611, 758972, 744040, 758969, 756400, 757244, 757149, 755291, 755542, 749585, 749191, 746336, 750521, 745796, 746944, 744844, 742882, 747914, 747248, 749955, 758218, 751973, 750509, 747791, 760650, 760140, 744951, 756792, 759848, 745138, 745220, 750345, 760595.

Skimmed for staff replies only (long complaint threads): 743683, 746480, 751339, 743531, 749259, 743661.

Fetched but not read in detail (no staff reply found by a quick scan): 744370, 743973, 744259, 748482, 749953, 743456 (opening post only), 760201, 758954.

Not loaded: the remaining ~100 threads of the ~200 listed (mostly "submission stuck/pending" reports). Collapsed "N more replies" sections were expanded only for 743063, 742882 and 747248; other threads may hide additional replies (e.g. 747519 "6 more replies", 746008 "5 more replies").

Thread 745748 (TFD-Agent) is a resource announcement with no measurements and no comments.
