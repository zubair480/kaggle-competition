# Gemma4 E4B Locate-Check-Submit v1

- Source: https://www.kaggle.com/code/apihpih/gemma4-e4b-locate-check-submit-v1
- Author: Apih Pih | votes: 1 | notebook version pulled: 5 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=[] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.06
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-e4b-it-qat-w4a16-ct; tools=[]; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=30, max_time_minutes=3.5, timeout_seconds=180, max_turns=80
  - sampling: temperature=1.0, top_p=0.95, max_output_tokens=4096, thinking_budget=2048, include_thoughts=false
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

E4B (small-model track), 3.5 min / 30 calls, temperature 1.0, thinking 2048. No score statement in the notebook text; see badge.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/sampling.yaml
- eval_config.yaml
- variants/F/agent.yaml
- variants/F/configs/sampling.yaml
- variants/F/eval_config.yaml
