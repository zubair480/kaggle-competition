# Patchsmith | Gemma 4 Developer Agent

- Source: https://www.kaggle.com/code/hanifnoerrofiq/patchsmith-gemma-4-developer-agent
- Author: Hanif Noer Rofiq | votes: 21 | notebook version pulled: 10 | last run: 2026-11-18
- Notebook settings: GPU=True TPU=False internet=False machine=NvidiaL4
- Inputs: datasets=[] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.2
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=40, max_time_minutes=8, timeout_seconds=60, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

Badge 0.2. Origin of the 'Patchsmith' prompt (6 tools, 60 s command timeout, 4-call/75-second finishing reserve, compile after last edit). Current pulled version (V11) uses max_tool_calls 40 and states 'No score or full-workload runtime has been measured for V11'. denpugovkin's exp021 (28 calls) reports 0.22 with the V7 recipe; evgendvorkin reproduction reports historical best 0.20, later 0.15 and 0.17.

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
