# Gemma4 SWE Agent T8 Static

- Source: https://www.kaggle.com/code/navyadevadiga/gemma4-swe-agent-t8-static
- Author: Navya Devadiga | votes: 76 | notebook version pulled: 5 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=[] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.2
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'submit_patch']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=25, max_time_minutes=8, timeout_seconds=240, max_turns=40
  - sampling: temperature=0.3, top_p=0.95, max_output_tokens=8192, thinking_budget=256, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

Badge 0.2. Author's own measurement in the notebook: 'public leaderboard 0.20 (submission of 2026-10-23), then 0.15 when the identical version was resubmitted (2026-10-28)'. Earlier variant Q256 with 4-min cap scored 0.15. Distinctive: only 3 tools (run_command, read_file, submit_patch; edits via python heredoc), thinking_budget 256, temperature 0.3, top_k 64, 25 calls, max_turns 40.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/system.md
