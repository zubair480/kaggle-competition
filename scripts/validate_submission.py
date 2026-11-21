"""Validate submission/ with the official validator (adk-submission + swegemma limits) plus our own checks.
Needs the harness wheels from the Kaggle dataset metric/gemma-4-developer-agent-wheelhouse installed.
usage: python scripts/validate_submission.py [submission_dir]"""
import re, sys
from pathlib import Path
from adk_submission import validate_directory
from adk_submission.discovery import discover_declared_models
from swegemma.config import build_submission_limits, MAX_SUBMISSION_SIZE_BYTES, ALLOWED_SUBMISSION_EXTENSIONS

sub = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "submission")
ALLOWED = {f"gemma-4-{m}-it-qat-w4a16-ct" for m in ("31b", "12b", "e4b", "e2b")}
limits, _ = build_submission_limits()
for p in sub.rglob("*"):
    assert not p.is_symlink(), f"symlink: {p}"
    if p.is_file():
        assert p.suffix.lower() in ALLOWED_SUBMISSION_EXTENSIONS, f"extension not allowed: {p}"
        txt = p.read_bytes()
        assert not re.search(rb"KGAT_|api[_-]?key\s*[:=]|BEGIN [A-Z ]*PRIVATE KEY", txt), f"possible credential in {p}"
        assert not re.search(rb"^diff --git |^\+\+\+ b/", txt, re.M), f"patch-like content in {p}"
        assert not re.search(rb"\b(fastapi|rich|requests|httpx)_\d{3,5}\b", txt), f"task id in {p}"
assert sum(p.stat().st_size for p in sub.rglob("*") if p.is_file()) < MAX_SUBMISSION_SIZE_BYTES
validate_directory(sub, limits=limits)
models = discover_declared_models(sub)
assert len(models) == 1 and next(iter(models)) in ALLOWED, models
print("OK:", sub, "model:", next(iter(models)))
