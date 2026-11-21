"""Offline analysis of the 129 public tasks -> data/task_analysis.csv, data/task_taxonomy.json.
Uses reference/test patches for research statistics only. Nothing here is shipped in the submission."""
import csv, json, re, sys, collections, statistics
from pathlib import Path

src = Path(sys.argv[1]); out = Path(__file__).resolve().parent.parent / "data"
tasks = [json.loads(l) for l in src.read_text().splitlines() if l.strip()]

def parse_patch(p):
    files = []; cur = None
    for line in p.splitlines():
        if line.startswith("+++ "):
            name = line[4:].strip(); name = name[2:] if name.startswith("b/") else name
            cur = dict(path=name, added=0, removed=0, hunks=0, new=False, funcs=set()); files.append(cur)
        elif line.startswith("--- ") and "/dev/null" in line:
            pass
        elif line.startswith("@@") and cur is not None:
            cur["hunks"] += 1
            m = re.search(r"@@.*@@\s*(?:async\s+)?(?:def|class)\s+(\w+)", line)
            if m: cur["funcs"].add(m.group(1))
            if re.match(r"@@ -0,0 ", line): cur["new"] = True
        elif cur is not None and line.startswith("+") and not line.startswith("+++"):
            cur["added"] += 1
            m = re.match(r"\+\s*(?:async\s+)?(?:def|class)\s+(\w+)", line)
            if m: cur["funcs"].add(m.group(1))
        elif cur is not None and line.startswith("-") and not line.startswith("---"):
            cur["removed"] += 1
    return files

def kind(path):
    if re.search(r"(^|/)(tests?|testing)/|(^|/)test_[^/]*\.py$|_test\.py$", path): return "test"
    if path.startswith(("docs/", "docs_src/")) or path.endswith((".md", ".rst", ".txt")): return "docs"
    if path.startswith((".github/", "scripts/")) or path.endswith((".toml", ".cfg", ".yml", ".yaml", ".ini", ".lock")): return "infra"
    return "src" if path.endswith((".py", ".pyi")) else "other"

CATS = [
 ("typing_annotations", r"\btyp(e|ing)\b|annotation|mypy|pydantic v2|Annotated|generic"),
 ("validation_errors", r"validat|invalid|raise[sd]?\b|exception|error message|ValueError|TypeError"),
 ("serialization_encoding", r"serializ|json|encod|decod|unicode|bytes|charset"),
 ("http_behavior", r"\bheader|cookie|redirect|status code|request|response|proxy|auth|url|ssl|timeout"),
 ("async_concurrency", r"async|await|thread|concurren|event loop|stream"),
 ("terminal_rendering", r"render|console|markup|ansi|color|style|table|panel|progress|wrap|width|emoji|traceback|syntax"),
 ("openapi_schema", r"openapi|schema|swagger|docs url|response_model"),
 ("dependency_injection", r"depend(s|ency)|inject|security scheme|oauth"),
 ("docs_examples", r"\bdocs?\b|tutorial|example|translation|typo"),
 ("tooling_ci", r"\bCI\b|workflow|release|lint|pre-commit|script|bump|upgrade|dependabot"),
 ("compat_deprecation", r"deprecat|compat|python 3\.\d+|support for|drop support|backward"),
 ("performance", r"perform|speed|slow|cache|memory"),
]

rows = []; tax = collections.Counter(); per_repo = collections.defaultdict(collections.Counter)
for t in tasks:
    gold = parse_patch(t["patch"]); test = parse_patch(t["test_patch"])
    kinds = collections.Counter(kind(f["path"]) for f in gold)
    src_files = [f for f in gold if kind(f["path"]) == "src"]
    text = t["problem_statement"]; low = text.lower()
    cats = [c for c, rx in CATS if re.search(rx, low, re.I)]
    # is the gold source file literally named in the issue? is a changed symbol named?
    file_named = any(f["path"] in text or Path(f["path"]).name in text for f in gold if kind(f["path"]) != "test")
    syms = set().union(*[f["funcs"] for f in gold]) if gold else set()
    sym_named = any(re.search(r"\b" + re.escape(s) + r"\b", text) for s in syms if len(s) > 3)
    added = sum(f["added"] for f in gold); removed = sum(f["removed"] for f in gold)
    nfiles = len(gold); new_files = sum(1 for f in gold if f["new"])
    title = text.strip().splitlines()[0][:120] if text.strip() else ""
    is_pr = bool(re.search(r"pull request|## pull request|this pr\b", low))
    ttype = ("feature" if re.search(r"\badd(s|ed)?\b|support|feature|allow|implement|new\b", title, re.I) else
             "bugfix" if re.search(r"fix|bug|error|crash|incorrect|wrong|regress", title, re.I) else
             "refactor/maintenance" if re.search(r"refactor|update|upgrade|bump|remove|clean|simplif|tweak|docs?|typo|translat|internal", title, re.I) else "other")
    size = added + removed
    diff = "easy" if (size <= 15 and nfiles <= 1) else "medium" if (size <= 80 and nfiles <= 3) else "hard"
    rows.append(dict(instance_id=t["instance_id"], repo=t["repo"], base_commit=t["base_commit"][:10], created_at=t["created_at"][:10],
        title=title, task_type=ttype, issue_chars=len(text), has_hints=bool(t["hints_text"].strip()), is_pr_description=is_pr,
        gold_files=nfiles, gold_src_files=len(src_files), gold_new_files=new_files, gold_added=added, gold_removed=removed,
        gold_hunks=sum(f["hunks"] for f in gold), gold_symbols=len(syms), file_kinds="|".join(f"{k}:{v}" for k, v in sorted(kinds.items())),
        cross_module=len({str(Path(f["path"]).parent) for f in gold}) > 1, gold_file_named_in_issue=file_named, gold_symbol_named_in_issue=sym_named,
        test_files=len(test), test_added=sum(f["added"] for f in test), categories="|".join(cats), difficulty_heuristic=diff,
        gold_paths="|".join(f["path"] for f in gold)))
    for c in cats: tax[c] += 1; per_repo[t["repo"]][c] += 1

out.mkdir(exist_ok=True)
with (out / "task_analysis.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def dist(key): return dict(collections.Counter(r[key] for r in rows).most_common())
def q(vals): vals = sorted(vals); return dict(median=statistics.median(vals), p75=vals[int(.75 * len(vals))], p90=vals[int(.9 * len(vals))], max=vals[-1])
summary = dict(n_tasks=len(rows), repos=dist("repo"), task_type=dist("task_type"), difficulty_heuristic=dist("difficulty_heuristic"),
    keyword_categories=dict(tax.most_common()), per_repo_categories={k: dict(v.most_common()) for k, v in per_repo.items()},
    gold_files=q([r["gold_files"] for r in rows]), gold_changed_lines=q([r["gold_added"] + r["gold_removed"] for r in rows]),
    issue_chars=q([r["issue_chars"] for r in rows]), test_added_lines=q([r["test_added"] for r in rows]),
    pct=dict(single_file=sum(r["gold_files"] == 1 for r in rows) / len(rows), creates_new_file=sum(r["gold_new_files"] > 0 for r in rows) / len(rows),
             cross_module=sum(r["cross_module"] for r in rows) / len(rows), has_hints=sum(r["has_hints"] for r in rows) / len(rows),
             gold_file_named_in_issue=sum(r["gold_file_named_in_issue"] for r in rows) / len(rows),
             gold_symbol_named_in_issue=sum(r["gold_symbol_named_in_issue"] for r in rows) / len(rows),
             is_pr_description=sum(r["is_pr_description"] for r in rows) / len(rows),
             touches_non_src_only=sum(r["gold_src_files"] == 0 for r in rows) / len(rows)),
    created_at=dict(min=min(r["created_at"] for r in rows), max=max(r["created_at"] for r in rows)),
    by_repo={repo: dict(n=len(rs), median_changed=statistics.median([r["gold_added"] + r["gold_removed"] for r in rs]),
                        median_files=statistics.median([r["gold_files"] for r in rs]), easy=sum(r["difficulty_heuristic"] == "easy" for r in rs),
                        medium=sum(r["difficulty_heuristic"] == "medium" for r in rs), hard=sum(r["difficulty_heuristic"] == "hard" for r in rs))
             for repo in dist("repo") for rs in [[r for r in rows if r["repo"] == repo]]})
(out / "task_taxonomy.json").write_text(json.dumps(summary, indent=1))
print(json.dumps(summary, indent=1))
