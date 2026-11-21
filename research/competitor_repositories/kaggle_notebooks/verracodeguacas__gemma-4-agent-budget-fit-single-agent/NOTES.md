# Gemma 4 Agent: Budget-Fit Single Agent

- Source: https://www.kaggle.com/code/verracodeguacas/gemma-4-agent-budget-fit-single-agent
- Author: Wilmer E. Henao | votes: 248 | notebook version pulled: 5 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=[] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.18
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch', 'get_code_neighbors', 'search_similar_code', 'get_code_subgraph']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=28, max_time_minutes=8, timeout_seconds=240, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: leoprovorov/score-to-gemma-4, matterhorn3838/gemma-gemini-the-ultimate-duo, xiuchisun/gemma-4-agent-budget-fit-31b-mainline, zbigniewkirchner/gemma-4-agent-run-your-agent-locally

## Evidence and comments

The root of the whole public family (single 31B agent, 28 calls / 8 min / 240 s, edit-by-call-12). Badge 0.18. Best-measured public config: dariushafshar reports mean 10.00/58 over 10 draws (95% CI 8.98-11.02) for V5 of this file set; dmitriigluzdov reports 8-11 solved over seven runs. Byte-identical bundles: leoprovorov/score-to-gemma-4 (badge 0.2), xiuchisun/gemma-4-agent-budget-fit-31b-mainline (0.2), zbigniewkirchner run-locally bundle A, dmitriigluzdov public-agent-ideas (0.18).

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/system.md
- variants/FILES/agent.yaml
- variants/FILES/configs/sampling.yaml
- variants/FILES/eval_config.yaml
- variants/FILES/prompts/system.md
