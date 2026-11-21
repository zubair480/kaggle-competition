# 🐈‍⬛ Can Gemma 4 Become a Software Engineer?

- Source: https://www.kaggle.com/code/evgendvorkin/can-gemma-4-become-a-software-engineer
- Author: Дворкин Евгений Владимирович | votes: 55 | notebook version pulled: 59 | last run: 2026-11-18
- Notebook settings: GPU=False TPU=False internet=False machine=None
- Inputs: datasets=['dariushafshar/gemma-4-agent-public-config-draws', 'metric/gemma-4-developer-agent-wheelhouse', 'prvsiyan/gemma-e07-verification-six-tools', 'prvsiyan/gemma-h0-endpoint-compatibility-kit', 'prvsiyan/gemma-reproducibility-wheels', 'evgendvorkin/okruzhenie555', 'evgendvorkin/topckor-0-22', 'evgendvorkin/topskor'] models=['google/gemma-4/Other/gemma-4-31b-it-qat-w4a16-ct/2'] kernels=[]
- Kaggle public-score badge on the competition Code tab (read 2026-11-21): 0.2
  - The badge is the notebook's best scored version; it may belong to an older version than the source saved here, and identical files re-score within roughly +/-3 tasks of 58.
- Key settings (from the saved files): model=gemma-4-31b-it-qat-w4a16-ct; tools=['run_command', 'read_file', 'edit_file', 'write_file', 'get_status', 'submit_patch']; adapter=no; sub_agents=no; skills=no
  - eval_config: max_tool_calls=28, max_time_minutes=8, timeout_seconds=60, max_turns=80
  - sampling: temperature=0.2, top_p=0.95, max_output_tokens=8192, thinking_budget=4096, include_thoughts=true
- Bundles with byte-identical agent.yaml + sampling + eval_config + system.md among pulled notebooks: denpugovkin/gemma-4-repair-lab-compare-before-you-submit

## Evidence and comments

Badge 0.2. Byte-identical to denpugovkin CONTROL (Patchsmith V5/exp021, 28 calls, 60 s commands). Notebook text: 'Our historical best 0.20', 'latest recorded public Version 52 returned 0.15', 'Latest scored submission Nov 21: 0.17'; upstream 0.22 is 'not ours'.

## Files

Extracted statically (no notebook code was executed) from string literals / FILES dictionaries / embedded archives in the notebook source. `variants/<NAME>/` holds each named bundle dictionary found in the notebook; root-level files are the last bundle assigned in the source. `_const_*.txt` are long prompt/YAML string constants that were not tied to a file path.

- agent.yaml
- configs/sampling.yaml
- eval_config.yaml
- prompts/system.md
- variants/CANDIDATE_FILES/LICENSE.txt
- variants/CANDIDATE_FILES/NOTICE.txt
- variants/CANDIDATE_FILES/agent.yaml
- variants/CANDIDATE_FILES/configs/sampling.yaml
- variants/CANDIDATE_FILES/eval_config.yaml
- variants/CANDIDATE_FILES/prompts/system.md
