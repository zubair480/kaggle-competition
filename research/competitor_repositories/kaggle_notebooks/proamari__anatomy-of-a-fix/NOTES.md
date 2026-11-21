# 🧬 Anatomy of a Fix

- Source: https://www.kaggle.com/code/proamari/anatomy-of-a-fix
- Author: Marina Afanaseva | votes: 17 | notebook version pulled: 6 | last run: 2026-11-18
- Notebook settings: GPU=True TPU=False internet=False machine=NvidiaTeslaT4
- Inputs: datasets=[] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): none seen
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch']; adapter=no; sub_agents=yes; skills=no
  - eval_config: max_tool_calls=not set, max_time_minutes=not set, timeout_seconds=not set, max_turns=not set
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=false
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

No score statement beyond the badge above was found in the notebook text.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/sampling.yaml
- prompts/analyzer.md
- prompts/system.md
- sub_agents/code_analyzer.yaml
- variants/FILES/agent.yaml
- variants/FILES/configs/sampling.yaml
- variants/FILES/prompts/analyzer.md
- variants/FILES/prompts/system.md
- variants/FILES/sub_agents/code_analyzer.yaml
