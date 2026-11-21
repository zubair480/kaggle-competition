"""Validate submission/ against the harness limits we know of and zip it."""
import re, sys, zipfile
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent / "submission"
ALLOWED_EXT = {".yaml", ".yml", ".md", ".txt", ".py", ".json", ".safetensors"}
MODELS = {f"gemma-4-{m}-it-qat-w4a16-ct" for m in ("31b", "12b", "e4b", "e2b")}
TOOLS = {"run_command", "read_file", "edit_file", "write_file", "get_status", "submit_patch",
         "get_code_neighbors", "search_similar_code", "get_code_subgraph"}


class Loader(yaml.SafeLoader):
    pass


def _include(loader, node):
    rel = loader.construct_scalar(node)
    assert ".." not in Path(rel).parts and not Path(rel).is_absolute(), rel
    p = Path(loader.name).parent / rel
    if p.suffix in (".md", ".txt"):
        return p.read_text(encoding="utf-8")
    with open(p) as fh:
        ld = Loader(fh)
        try:
            return ld.get_single_data()
        finally:
            ld.dispose()


Loader.add_constructor("!include", _include)


def load(p):
    with open(p) as fh:
        ld = Loader(fh)
        try:
            return ld.get_single_data()
        finally:
            ld.dispose()


def main():
    files = [p for p in ROOT.rglob("*") if p.is_file()]
    for p in files:
        assert p.suffix in ALLOWED_EXT, f"disallowed file type: {p}"
        assert not p.is_symlink(), p
    assert sum(p.stat().st_size for p in files) < 3 * 2**30
    agent = load(ROOT / "agent.yaml")
    assert agent["model"] in MODELS, agent["model"]
    assert agent["instruction"].strip()
    for t in agent["tools"]:
        assert t in TOOLS, t
    # ADK treats {name} in instructions as session-state templates.
    bad = set(re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", agent["instruction"])) - {"problem_description", "hints"}
    assert not bad, f"unexpected template variables in prompt: {bad}"
    g = agent["generate_content_config"]
    assert 1 <= g["max_output_tokens"] <= 32768
    assert 0 <= g["thinking_config"]["thinking_budget"] <= 32768
    ev = load(ROOT / "eval_config.yaml")["evaluation"]
    assert set(ev) <= {"timeout_seconds", "max_tool_calls", "max_time_minutes", "max_turns"}
    assert ev["max_time_minutes"] <= 5, "12h total limit: keep the per-task cap at 5 min or less"
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "submission.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            z.write(p, p.relative_to(ROOT).as_posix())
    print(f"ok: {len(files)} files, prompt {len(agent['instruction'])} chars -> {out}")


if __name__ == "__main__":
    main()
