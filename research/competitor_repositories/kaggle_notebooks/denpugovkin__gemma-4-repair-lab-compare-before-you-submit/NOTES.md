# Gemma 4 Repair Lab: Compare Before You Submit

- Source: https://www.kaggle.com/code/denpugovkin/gemma-4-repair-lab-compare-before-you-submit
- Author: Den Pugovkin | votes: 158 | notebook version pulled: 9 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=['metric/gemma-4-developer-agent-wheelhouse'] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.22
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=28, max_time_minutes=8, timeout_seconds=60, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: evgendvorkin/can-gemma-4-become-a-software-engineer

## Evidence and comments

Badge 0.22. Notebook text: 'Preserved incumbent: our exp021 public 0.22, Version 5'; exp023 (larger output ceiling) and exp024 (new-file verification paragraph) 'both received public 0.12'; a status-policy trial scored 0.17. variants/CONTROL_FILES = the scored exp021 incumbent (6 tools, 28 calls, 8 min, command timeout 60 s, Patchsmith prompt). variants/CANDIDATE_FILES (root files) = same with max_tool_calls 40, explicitly UNSCORED. Prompt is the Patchsmith V7 recipe (hanifnoerrofiq).

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/system.md
- variants/CANDIDATE_FILES/LICENSE.txt
- variants/CANDIDATE_FILES/NOTICE.txt
- variants/CANDIDATE_FILES/agent.yaml
- variants/CANDIDATE_FILES/configs/sampling.yaml
- variants/CANDIDATE_FILES/eval_config.yaml
- variants/CANDIDATE_FILES/prompts/system.md
- variants/CONTROL_FILES/LICENSE.txt
- variants/CONTROL_FILES/NOTICE.txt
- variants/CONTROL_FILES/agent.yaml
- variants/CONTROL_FILES/configs/sampling.yaml
- variants/CONTROL_FILES/eval_config.yaml
- variants/CONTROL_FILES/prompts/system.md
