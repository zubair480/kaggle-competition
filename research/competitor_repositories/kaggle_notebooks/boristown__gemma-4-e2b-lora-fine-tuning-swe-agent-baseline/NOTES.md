# Gemma 4 E2B LoRA Fine-Tuning & SWE-Agent Baseline

- Source: https://www.kaggle.com/code/boristown/gemma-4-e2b-lora-fine-tuning-swe-agent-baseline
- Author: 暗黑AGI | votes: 72 | notebook version pulled: 23 | last run: 2026-11-18
- Notebook settings: GPU=True TPU=False internet=False machine=NvidiaL4
- Inputs: datasets=['metric/gemma-4-developer-agent-wheelhouse', 'dmitriigluzdov/gemma-4-serving-and-lora-verification-kit'] models=['google/gemma-4/Transformers/gemma-4-e4b-it/1', 'google/gemma-4/Other/gemma-4-e2b-it-qat-w4a16-ct/2', 'google/gemma-4/Other/gemma-4-e4b-it-qat-w4a16-ct/2', 'google/gemma-4/Other/gemma-4-31b-it-qat-w4a16-ct/2', 'google/gemma-4/Transformers/gemma-4-e2b-it/1'] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.17
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model={TARGET_MODEL}; tools=['run_command', 'read_file', 'edit_file', 'get_status', 'submit_patch']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=36, max_time_minutes=7.5, timeout_seconds=240, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=4096, thinking_budget=2048, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

Badge 0.17; notebook text claims 'V21 (21/60, LB 0.15-0.17)'. Despite the title, the submitted bundle is 31B with a 'surgical' LoRA: r=8, alpha=2 (scale 0.25), q_proj+o_proj on layers 48-59 only. Local eval: 60 public tasks on 4xL4 in ~5.5 h using official VllmServer(tp=4) + swegemma Evaluator at 7.5 min / 36 calls / 80 turns / 240 s.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/system.md
