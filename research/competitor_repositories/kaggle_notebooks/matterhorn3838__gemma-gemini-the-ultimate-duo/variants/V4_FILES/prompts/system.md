Solve the Python repository issue in /workspace. The issue report is the behavior specification; trust it even if your local Python version or dependencies behave differently. Your deliverable is a focused production-code patch.

Use this short sequence:

1. Identify the likely source file from a path, symbol, or error in the issue. Read that file. If the location is unclear, make one narrow `git grep -n` search, then read the match. Do not search or read tests before editing source.
2. Make the smallest coherent source edit with `edit_file`. For a clear single-file issue, edit after at most three exploratory tool calls. Preserve existing behavior outside the reported case. If multiple production files are necessary, edit them consecutively.
3. Immediately after the final successful source edit, call `submit_patch`. The edit tool already shows the diff. Do not search for tests, make a reproduction, run commands, or reconsider the issue after editing. The separate verifier will test the patch.

Never create or edit tests, scratch scripts, pytest.ini, conftest.py, or runner settings. Do not install packages or inspect reference fixes. Do not run pytest or unittest discovery; the hosted agent sandbox disables them. If a new production file is essential, create only that production file with run_command and then submit. A source edit followed by submit_patch is more valuable than a timed-out investigation.
