---
name: repo-scout
description: Bounded Python repository localization and targeted verification. Evidence Scout combines identifier, error-message, behavior and full-issue searches; its ranked locations include short source evidence. Existing show, tests and check helpers remain available.
---
# repo-scout

Use `run_skill_script`, skill_name `repo-scout`, with `args` mapping option names to values.

- `scripts/locate.py`, option `query`: the full issue text, up to 6,000 characters. Run once first. It combines up to four BM25 views with reciprocal-rank fusion, deduplicates symbols, and prints at most ten source locations with short evidence. The identifiers and quoted messages come only from the supplied issue. Confirm the diagnosis by reading the source; retrieval ranks are not probabilities. If it has no useful match or fails, use `run_command` with exact identifiers or `search_similar_code`. It excludes tests, caches, symlinks and build directories. A bounded index may be incomplete.
- `scripts/show.py`, option `name`; optional `path`: print a definition with line numbers. Use `read_file` if no definition is found.
- `scripts/tests.py`, option `name`: list existing tests mentioning a symbol or module.
- `scripts/check.py`, options `files` (comma-separated) and `tests` (space-separated pytest targets); optional `k` and `timeout`: compile changed files and run targeted tests. Read the verdict, not just tool execution status. Compilation may create bytecode caches. Do not alter tests or install packages to repair the environment.

Localization is read-only and uses only the checked-out source and issue text. No model downloads, network calls, hidden labels, or solution patches are used by these scripts.
