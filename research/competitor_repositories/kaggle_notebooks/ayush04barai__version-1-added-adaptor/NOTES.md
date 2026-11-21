# Version 1 added Adaptor

- Source: https://www.kaggle.com/code/ayush04barai/version-1-added-adaptor
- Author: Ayush Barai | votes: 115 | notebook version pulled: 9 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=[] models=[] kernels=['ayush04barai/lora-step-2']
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.22
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch', 'get_code_neighbors', 'search_similar_code', 'get_code_subgraph']; adapter=yes; sub_agents=no; skills=no
  - eval_config: max_tool_calls=28, max_time_minutes=8, timeout_seconds=240, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=6144, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

Badge 0.22, but the notebook text says 'your usual range is 0.12 to 0.22' for the SAME files WITHOUT the adapter and gives no score for the adapter version - so 0.22 cannot be attributed to the LoRA. Bundle = Budget-Fit-style prompt + `adapter: main_lora` (max_output_tokens 6144). Adapter comes from kernel output ayush04barai/lora-step-2: rank 16, alpha 16, layers 30-59 only, targets q_proj/o_proj/down_proj, lr 2e-4, 4 h on L4, bitsandbytes NF4 4-bit over google/gemma-4 Transformers 'gemma-4-31b-it-qat-q4_0-unquantized' v2, trained only on edit_file calls on source files from resolved runs in dataset dmitriigluzdov/gemma-4-serving-and-lora-verification-kit (Gemma native + Qwen trajectories). Adapter weights are not in the notebook source (read from the kernel output).

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
