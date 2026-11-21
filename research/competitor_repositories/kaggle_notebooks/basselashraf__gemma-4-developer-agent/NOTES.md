# Gemma 4 Developer Agent

- Source: https://www.kaggle.com/code/basselashraf/gemma-4-developer-agent
- Author: Bassel Elbahnasy | votes: 4 | notebook version pulled: 10 | last run: 2026-11-18
- Notebook settings: GPU=True TPU=False internet=False machine=NvidiaL4
- Inputs: datasets=['metric/gemma-4-developer-agent-wheelhouse'] models=['google/gemma-4/Other/gemma-4-31b-it-qat-w4a16-ct/2'] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.2
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=?; tools=[]; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=not set, max_time_minutes=not set, timeout_seconds=not set, max_turns=not set
  - sampling: temperature=not set, top_p=not set, max_output_tokens=not set, thinking_budget=not set, include_thoughts=not set
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

No score statement beyond the badge above was found in the notebook text.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- _const_BUDGET_PROMPT_15.txt
- _const_CHAMPION_PROMPT.txt
- _const_REPAIR_PROMPT.txt
