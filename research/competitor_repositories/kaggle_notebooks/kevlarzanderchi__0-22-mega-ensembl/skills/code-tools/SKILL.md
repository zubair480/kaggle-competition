---
name: code-tools
description: Fast offline helpers for this repository. locate ranks the source files and lines most likely to need the change for the issue (exact-name grep, definitions and test imports fused). check compiles your edit and runs the one closest test file.
---
# code-tools

Call `run_skill_script` with `skill_name` `code-tools` and:

| file_path | args | Returns |
|---|---|---|
| `scripts/locate.py` | `{"issue": "<key sentences, exact names, error messages>"}` | up to 6 likely source files, best first, each with its matching lines (`[def]` marks a definition), and the tests that mention those names |
| `scripts/check.py` | `{}` (optional `{"k": "test_name"}`) | syntax check of every changed file, PASS/FAIL of the closest existing test file (90 s cap), and the diff stat |

Both finish in seconds and print under 4,000 characters. After locate, read the top file at the printed lines with `read_file`. After check: fix once if your change broke something, otherwise call `submit_patch`.
