# gemma4-agent1

- Source: https://www.kaggle.com/code/spiritofvishwakarma/gemma4-agent1
- Author: Aditya Vishwakarma | votes: 9 | notebook version pulled: 32 | last run: 2026-11-18
- Notebook settings: GPU=True TPU=False internet=False machine=NvidiaL4
- Inputs: datasets=['', 'metric/gemma-4-developer-agent-wheelhouse'] models=['google/gemma-4/Other/gemma-4-31b-it-qat-w4a16-ct/2'] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.18
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch', 'get_code_subgraph']; adapter=yes; sub_agents=yes; skills=no
  - eval_config: max_tool_calls=not set, max_time_minutes=not set, timeout_seconds=150, max_turns=70
  - sampling: temperature=0.9, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

Badge 0.18. Starter-like analyzer+coder with sample adapters declared, temperature 0.9.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- _const_SYSTEM_PROMPT.txt
- agent.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/analyzer.md
