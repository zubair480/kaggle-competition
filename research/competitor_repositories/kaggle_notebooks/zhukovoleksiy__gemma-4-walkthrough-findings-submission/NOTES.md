# Gemma 4 | Walkthrough, Findings & Submission

- Source: https://www.kaggle.com/code/zhukovoleksiy/gemma-4-walkthrough-findings-submission
- Author: Oleksii Zhukov | votes: 101 | notebook version pulled: 8 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=['metric/gemma-4-developer-agent-wheelhouse'] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.15
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch', 'get_code_neighbors', 'search_similar_code', 'get_code_subgraph']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=28, max_time_minutes=7, timeout_seconds=240, max_turns=80
  - sampling: temperature=1.0, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: none

## Evidence and comments

Badge 0.15. Analyzer + coder, temperature 1.0, 7 min / 28 calls. hitarthjain0 cites this author: a 4.5-minute cap took about 10 hours in a scored run.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/analyzer.md
- prompts/system.md
- sub_agents/code_analyzer.yaml
- variants/V2_FILES/agent.yaml
- variants/V2_FILES/configs/sampling.yaml
- variants/V2_FILES/prompts/analyzer.md
- variants/V2_FILES/prompts/system.md
- variants/V2_FILES/sub_agents/code_analyzer.yaml
- variants/V3_FILES/agent.yaml
- variants/V3_FILES/configs/sampling.yaml
- variants/V3_FILES/eval_config.yaml
- variants/V3_FILES/prompts/analyzer.md
- variants/V3_FILES/prompts/system.md
- variants/V3_FILES/sub_agents/code_analyzer.yaml
- variants/V4_FILES/agent.yaml
- variants/V4_FILES/configs/sampling.yaml
- variants/V4_FILES/eval_config.yaml
- variants/V4_FILES/prompts/system.md
