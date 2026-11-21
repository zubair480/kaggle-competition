# MUHAMMED IDRIS BIN YACOOB, v24 (leaderboard 0.24)

Read 2026-11-21. Source: Kaggle dataset `muhammedidris28/gemma4-agent-runs` (Apache-2.0, published for the
paper track) and the replica notebook `cosmorin/gemma-4-idris-v24-e07-faithful-replica`. Files copied to
`idris_v24/` (bundle, the author's leaderboard ledger, dataset README).

## The 0.24 bundle

- Single `gemma-4-31b-it-qat-w4a16-ct` agent, 6 tools, no sub-agents, no adapter, no graph tools.
- 28 calls / 8 minutes / 240 s command timeout / 80 turns.
- Sampling: **temperature 1.0, top_p 0.95, top_k 64**, max output 8192, thinking 4096 with summaries.
- 3,240-byte prompt: copy the issue's exact terms, one specific grep, reads up to 120 lines, edit by call 12,
  one check and one repair, always `submit_patch` even if the local check is red.

## The author's own leaderboard ledger (one draw each unless two values)

v1 0.06, v4 0.08, v8 0.05, v10 0.05, v11-v13 0.12 (sub-agents: locator + coder), v16 0.08, v17 0.17 and 0.13,
v18 0.15, v19 0.18, **v24 0.24**, v25 0.15, v27 0.15, v30 0.17, v35 0.17. v29 and v37 exceeded the scorer's
time limit and got no score.

- v19 to v24 differs only in sampling (temperature 0.2 to 1.0, top_k 64 added). 0.18 to 0.24 is 3.5 tasks of
  58, one draw each, so it is within reported run-to-run noise.
- Every later version (40 calls at 8 minutes, adapters) scored 0.15-0.17 or timed out. The author never
  scored above 0.18 again.
- The same version scored 0.17 and 0.13 on two draws (v17).

## Their local runs (`runs.jsonl`, 1,514 task runs)

- v19 on their two 23-task sound splits: 8/23 and 11/23, 6 and 2 empty patches, mean 331 s and 262 s.
- v24 on 66 held-out practice tasks: 23/66, 11 empty patches, mean 407 s.
- Sub-agent versions (v11-v15) on 40 tasks: 4-8 resolved, 8-21 empty patches.

## What to take from it

1. Confirmed again: single agent, no sub-agents, no adapter. Their sub-agent and adapter versions scored lower.
2. Temperature 1.0 with top_k 64 is the one setting we have not tried. Evidence is a single draw.
3. 40 calls at 8 minutes cost them two submissions to the time limit. Our 5-minute cap avoids that.
4. Empty patches are a shared weakness (about a quarter of runs), not something specific to our agent.
