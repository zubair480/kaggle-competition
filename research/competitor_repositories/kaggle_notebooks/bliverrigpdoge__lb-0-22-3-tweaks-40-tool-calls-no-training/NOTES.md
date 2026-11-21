# # LB 0.22 | 3 tweaks, 40 tool calls, no training

- Source: https://www.kaggle.com/code/bliverrigpdoge/lb-0-22-3-tweaks-40-tool-calls-no-training
- Author: Mikkel Chávez Petersen | votes: 114 | notebook version pulled: 3 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=[] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.22
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch', 'get_code_neighbors', 'search_similar_code', 'get_code_subgraph']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=40, max_time_minutes=8, timeout_seconds=240, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: victorzhong0110/gemma4-pack-lb-0-22-40-tool-calls

## Evidence and comments

Title claim 'LB 0.22'; Kaggle badge 0.22. Budget-Fit V5 + three changes: max_tool_calls 28->40, fast exit (reply 'Done' after submit_patch; submit when call budget exhausted), and the issue pinned into the system prompt via ADK state placeholders `{problem_description}` / `{hints?}` so it survives history compaction. Single draw. NOTE alexust reports his own 40-call/8-min bundle exceeded the 12 h runtime; denpugovkin copies the 40-call idea as an unscored candidate. Byte-identical: victorzhong0110/gemma4-pack-lb-0-22-40-tool-calls.

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
