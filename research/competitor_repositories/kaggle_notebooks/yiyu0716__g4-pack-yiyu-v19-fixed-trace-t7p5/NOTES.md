# g4-pack-yiyu-v19-fixed-trace-t7p5

- Source: https://www.kaggle.com/code/yiyu0716/g4-pack-yiyu-v19-fixed-trace-t7p5
- Author: yiyu0716 | votes: 7 | notebook version pulled: 2 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=[] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.17
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'get_status', 'submit_patch']; adapter=no; sub_agents=yes; skills=yes
  - eval_config: max_tool_calls=100, max_time_minutes=7.5, timeout_seconds=300, max_turns=120
  - sampling: temperature=1.0, top_p=0.95, max_output_tokens=2048, thinking_budget=4096, include_thoughts=false
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

Badge 0.17 (also cited as public 0.17 by hitarthjain0). Only skill-based public bundle with a score: analyzer sub-agent workflow + coder, temperature 1.0, include_thoughts false, max_output_tokens 2048, 7.5 min / 100 calls / 120 turns, and an ADK skill `g4-edit` shipping .py scripts (SEARCH/REPLACE editor with syntax check, --trace, --check) run through run_skill_script. Files decoded from the base64 zip embedded in the notebook.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/analyzer_sampling.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/analyzer.md
- prompts/system.md
- skills/g4-edit/SKILL.md
- skills/g4-edit/scripts/g4edit.py
- skills/g4-edit/scripts/install.py
- sub_agents/code_analyzer.yaml
- sub_agents/workflow.yaml
