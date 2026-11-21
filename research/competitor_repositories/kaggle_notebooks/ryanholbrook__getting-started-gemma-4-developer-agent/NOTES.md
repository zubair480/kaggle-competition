# Getting Started - Gemma 4 Developer Agent (official starter, pinned)

- Source: https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent
- Author: Ryan Holbrook (Kaggle staff) | votes: 2963 | last run 2026-10-12
- Notebook settings: GPU on (machine shape NvidiaL4), internet off
- Inputs: dataset metric/gemma-4-developer-agent-wheelhouse; models google/gemma-4 Other/{31b,12b,e4b,e2b}-it-qat-w4a16-ct version 2; competition data
- No agent bundle is defined in the notebook: it copies `sample_submission/` from the competition data and only rewrites `model:` (default in the notebook: gemma-4-12b-it-qat-w4a16-ct) and strips `adapter:` lines / `adapters/` when the model is not 31B.
- No leaderboard score is stated in the notebook.
- `notebook_cells.txt` is the verbatim cell source. See ../kaggle_notebooks.md, section "Starter notebook".
