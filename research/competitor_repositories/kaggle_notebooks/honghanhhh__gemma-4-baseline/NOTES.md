# Gemma 4 Baseline

- Source: https://www.kaggle.com/code/honghanhhh/gemma-4-baseline
- Author: Hanh Tran | votes: 77 | notebook version pulled: 8 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=[] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.18
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch', 'get_code_neighbors', 'search_similar_code', 'get_code_subgraph']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=28, max_time_minutes=8, timeout_seconds=240, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: kawh1111/g4-baseline-024, mohanrajvelu/gemma-agent-submission-v1, saudmasaud/gemma4-exact-hong-024-baseline, shipship/gemma-4-baseline-lb-0-24-fork, victorzhong0110/gemma4-submission-pack-upstream-v8

## Evidence and comments

Formerly titled 'Gemma 4 Baseline | LB 0.24' (title claim by author; cited as 0.24 by hitarthjain0, alexust, saudmasaud, shipship). Current Kaggle badge: 0.18. Pulled source header says 'v6 (0.22 config, prompt-only edits)' built on flexonafft v2 and notes 'v5 lowered those limits and scored 0.13'. The system.md here is byte-identical to the bundles others label 'exact Hong 0.24' (saudmasaud/gemma4-exact-hong-024-baseline, kawh1111/g4-baseline-024, victorzhong0110/...upstream-v8 badge 0.2, shipship/...lb-0-24-fork badge 0.15, mohanrajvelu 0.17). Reproductions: alexust got 'exceeded the allowed runtime' on byte-identical bytes, 0.17 with one extra prompt line, 0.15 with 7-min cap; carsonrodrigues resubmitted unchanged twice and hit the 12-hour limit both times. Treat 0.24 as a single lucky draw of a config that sits on the 12 h edge.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/system.md
