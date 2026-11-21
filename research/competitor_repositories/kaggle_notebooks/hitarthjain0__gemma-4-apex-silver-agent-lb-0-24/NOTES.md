# Gemma 4 Apex Silver Agent LB 0 24

- Source: https://www.kaggle.com/code/hitarthjain0/gemma-4-apex-silver-agent-lb-0-24
- Author: Hitarth Jain | votes: 1 | notebook version pulled: 1 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=[] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): none seen
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=28, max_time_minutes=8, timeout_seconds=240, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: hitarthjain0/gemma-4-patch-berserker-evaluate-then-submit, jingshuifu/gemma-4-dev-agent-lb024, shipship/gemma-4-dev-agent-lb024-fork

## Evidence and comments

Title claim 'LB 0.24 ~ 0.26+ | Silver Target' is NOT a measured score of this notebook: it credits honghanhhh for 0.24. Same prompt as jingshuifu/gemma-4-dev-agent-lb024 (badge 0.15) and shipship/gemma-4-dev-agent-lb024-fork (badge 0.18).

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
