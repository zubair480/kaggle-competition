---
name: g4-edit
description: Installs /tmp/g4edit.py, the checked SEARCH/REPLACE editor for source files, used through run_command.
---

Install once per task: call run_skill_script with skill_name = g4-edit and
file_path = scripts/install.py (plain values, no other arguments). It prints INSTALLED,
and /tmp/g4edit.py then stays available for the whole task.

Then make each source edit with one `run_command` call:

```
python3 /tmp/g4edit.py path/to/file.py <<'EDIT'
<<<<<<< SEARCH
exact current lines (copied verbatim, with indentation)
=======
replacement lines
>>>>>>> REPLACE
EDIT
```

- SEARCH must match the current file exactly once; keep it short but unique and
  never include line numbers. Several blocks for the same file may follow each other.
- An empty SEARCH section creates a new file.
- The editor checks Python syntax and rejects test files. On any error it leaves
  the file unchanged and prints why (`NOT_APPLIED`); fix the text and retry.
- `python3 /tmp/g4edit.py --trace /tmp/repro.py` lists the repository functions a
  reproduction executes and where an exception passes.
- Before `submit_patch`, run `python3 /tmp/g4edit.py --check`: it restores changed test
  files, deletes scratch files, names the closest existing tests and shows the diff.
