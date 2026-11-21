# Gemma 4 Developer Agent: Direct Code Verifier

- Source: https://www.kaggle.com/code/nihilisticneuralnet/gemma-4-developer-agent-direct-code-verifier
- Author: parthenos | votes: 16 | notebook version pulled: 26 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=[''] models=['google/gemma-4/Other/gemma-4-31b-it-qat-w4a16-ct/2'] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.17
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch', 'get_code_neighbors', 'search_similar_code', 'get_code_subgraph']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=28, max_time_minutes=8, timeout_seconds=240, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

Badge 0.17. 'Verifier' here is a prompt-level self-check, not a second model pass; variants/BASELINE_FILES is the flexonafft v2 bundle.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/system.md
- variants/BASELINE_FILES/agent.yaml
- variants/BASELINE_FILES/configs/sampling.yaml
- variants/BASELINE_FILES/eval_config.yaml
- variants/BASELINE_FILES/prompts/system.md
