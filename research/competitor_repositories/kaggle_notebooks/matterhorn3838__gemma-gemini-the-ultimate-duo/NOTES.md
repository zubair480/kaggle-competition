# Gemma + Gemini - The Ultimate Duo

- Source: https://www.kaggle.com/code/matterhorn3838/gemma-gemini-the-ultimate-duo
- Author: Matterhorn3838 | votes: 40 | notebook version pulled: 4 | last run: 2026-11-18
- Notebook settings: GPU=True TPU=False internet=False machine=NvidiaTeslaT4
- Inputs: datasets=['dmitriigluzdov/gemma-4-serving-and-lora-verification-kit', 'dmitriigluzdov/gemma-4-task-soundness-and-local-results'] models=[] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.18
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch', 'get_code_neighbors', 'search_similar_code', 'get_code_subgraph']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=28, max_time_minutes=8, timeout_seconds=240, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: leoprovorov/score-to-gemma-4, verracodeguacas/gemma-4-agent-budget-fit-single-agent, xiuchisun/gemma-4-agent-budget-fit-31b-mainline, zbigniewkirchner/gemma-4-agent-run-your-agent-locally

## Evidence and comments

Badge 0.18. Contains several variant bundles (BF_FILES = Budget-Fit; V4_FILES; analyzer/reconcile/review sub-agent configs). Text reports Roman Rozen's coder-analyzer archive at 0.12 (author report) and their own verified repeats 0.10 and 0.06; 114 of 129 public tasks judged sound.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/reconcile.yaml
- configs/review.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/analyzer.md
- prompts/contract.md
- prompts/reconcile.md
- prompts/symbol.md
- prompts/system.md
- sub_agents/code_analyzer.yaml
- sub_agents/contract.yaml
- sub_agents/panel.yaml
- sub_agents/parallel.yaml
- sub_agents/reconcile.yaml
- sub_agents/symbol.yaml
- variants/BF_FILES/agent.yaml
- variants/BF_FILES/configs/sampling.yaml
- variants/BF_FILES/eval_config.yaml
- variants/BF_FILES/prompts/system.md
- variants/FILES/ATTRIBUTION.md
- variants/FILES/LICENSE.txt
- variants/FILES/agent.yaml
- variants/FILES/configs/reconcile.yaml
- variants/FILES/configs/review.yaml
- variants/FILES/configs/sampling.yaml
- variants/FILES/eval_config.yaml
- variants/FILES/prompts/contract.md
- variants/FILES/prompts/reconcile.md
- variants/FILES/prompts/symbol.md
- variants/FILES/prompts/system.md
- variants/FILES/sub_agents/contract.yaml
- variants/FILES/sub_agents/panel.yaml
- variants/FILES/sub_agents/parallel.yaml
- variants/FILES/sub_agents/reconcile.yaml
- variants/FILES/sub_agents/symbol.yaml
- variants/REFERENCE_FILES/agent.yaml
- variants/REFERENCE_FILES/configs/sampling.yaml
- variants/REFERENCE_FILES/prompts/analyzer.md
- variants/REFERENCE_FILES/prompts/system.md
- variants/REFERENCE_FILES/sub_agents/code_analyzer.yaml
- variants/V4_FILES/agent.yaml
- variants/V4_FILES/configs/sampling.yaml
- variants/V4_FILES/eval_config.yaml
- variants/V4_FILES/prompts/system.md
