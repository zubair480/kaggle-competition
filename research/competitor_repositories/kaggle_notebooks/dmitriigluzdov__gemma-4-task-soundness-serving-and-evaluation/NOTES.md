# Gemma 4: Task Soundness, Serving and Evaluation

- Source: https://www.kaggle.com/code/dmitriigluzdov/gemma-4-task-soundness-serving-and-evaluation
- Author: Dmitrii Gluzdov | votes: 119 | notebook version pulled: 21 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=['dmitriigluzdov/gemma-4-serving-and-lora-verification-kit', 'dmitriigluzdov/gemma-4-task-soundness-and-local-results'] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.18
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch', 'get_code_neighbors', 'search_similar_code', 'get_code_subgraph']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=28, max_time_minutes=8, timeout_seconds=240, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=8192, thinking_budget=2048, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

No score statement beyond the badge above was found in the notebook text.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/system.md
- variants/ISSUE_CONTRACT_FILES/ATTRIBUTION.md
- variants/ISSUE_CONTRACT_FILES/LICENSE.txt
- variants/ISSUE_CONTRACT_FILES/agent.yaml
- variants/ISSUE_CONTRACT_FILES/configs/sampling.yaml
- variants/ISSUE_CONTRACT_FILES/eval_config.yaml
- variants/ISSUE_CONTRACT_FILES/prompts/system.md
- variants/REFERENCE_FILES/agent.yaml
- variants/REFERENCE_FILES/configs/sampling.yaml
- variants/REFERENCE_FILES/eval_config.yaml
- variants/REFERENCE_FILES/prompts/system.md
- variants/THINKING_FILES/agent.yaml
- variants/THINKING_FILES/configs/sampling.yaml
- variants/THINKING_FILES/eval_config.yaml
- variants/THINKING_FILES/prompts/system.md
