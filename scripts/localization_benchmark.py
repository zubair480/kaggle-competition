"""Offline localization benchmark on the public tasks (model-free).

Corpus: the functions/classes in the official pre-computed code graph of each task snapshot.
Gold: source files touched by the reference patch (offline research only; never shipped).
Strategies: identifier grep, BM25, the harness' own search_similar_code backend, and rank fusion.
usage: python scripts/localization_benchmark.py DATA_DIR OUT.json
"""
import json, math, re, sys, collections, time
from pathlib import Path

data = Path(sys.argv[1]); out = Path(sys.argv[2])
tasks = [json.loads(l) for l in (data / "tasks.jsonl").read_text().splitlines() if l.strip()]
TEST_RX = re.compile(r"(^|/)(tests?|testing)/|(^|/)test_[^/]*\.py$|_test\.py$|(^|/)conftest\.py$")
STOP = set("the a an and or of to in is it this that for with on as be are was not if when from by at we you can should would will have has but which there their they them then than into out about how what why does do did use used using also only more some any all new add adds added fix fixes fixed issue pull request please code python file files error example following expected actual behavior version description".split())

def gold_src(patch):
    fs = [m.group(1) for m in re.finditer(r"^\+\+\+ b/(\S+)", patch, re.M)]
    fs += [m.group(1) for m in re.finditer(r"^\+\+\+ (?!b/|/dev/null)(\S+)", patch, re.M)]
    return sorted({f for f in fs if f.endswith(".py") and not TEST_RX.search(f)})

def identifiers(text):
    ids = []
    for m in re.finditer(r"`([^`\n]{2,80})`", text):
        ids += re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", m.group(1))
    ids += re.findall(r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+\b", text)            # CamelCase
    ids += re.findall(r"\b[a-z0-9]+(?:_[a-z0-9]+)+\b", text)                     # snake_case
    ids += [p for m in re.finditer(r"\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+\b", text) for p in m.group(0).split(".")]
    seen, res = set(), []
    for i in ids:
        if i.lower() not in STOP and len(i) > 2 and i not in seen:
            seen.add(i); res.append(i)
    return res

def tok(s): return [w for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]+", s.lower()) if w not in STOP]

def node_file(name, modules):
    parts = name.split(".")
    for n in range(len(parts), 0, -1):
        p = "/".join(parts[:n])
        if p in modules: return modules[p]
    return None

def load_corpus(task):
    short = task["repo"].split("/")[-1]
    gp = data / "graphs" / f"{short}_{task['base_commit']}.json"
    if not gp.exists(): return None
    g = json.loads(gp.read_text())
    return g["nodes"]

def rank_files(scores): return [f for f, _ in sorted(scores.items(), key=lambda kv: -kv[1])]

import swegemma.graph as sg
res = []; agg = collections.defaultdict(lambda: collections.defaultdict(list)); t_graph = []; empty_graph = 0; graph_q = 0
for task in tasks:
    gold = gold_src(task["patch"])
    nodes = load_corpus(task)
    if not gold or nodes is None: continue
    # file <- nodes. Node names are dotted module paths + qualname; group by longest module prefix seen as a top-level def owner.
    files = collections.defaultdict(list)
    for n in nodes:
        name = n["name"]; parts = name.split(".")
        # heuristic module path: drop trailing CamelCase/func parts until the remainder matches another node's prefix set
        files[name].append(n.get("text") or "")
    names = list(files)
    # candidate file paths = every dotted prefix that equals a gold path or is the longest common module prefix
    def to_file(name):
        parts = name.split(".")
        for n in range(len(parts) - 1, 0, -1):
            cand = "/".join(parts[:n]) + ".py"
            if cand in known_files: return cand
        return "/".join(parts[:-1]) + ".py"
    # known module files: prefixes that have >=1 direct child whose text starts with def/class at column 0
    known_files = set()
    for n in nodes:
        parts = n["name"].split(".")
        txt = (n.get("text") or "").lstrip()
        if txt.startswith(("def ", "async def ", "class ", "@")) and len(parts) >= 2:
            # top-level symbol if no shorter prefix is itself a class node
            pass
    prefix_is_symbol = {n["name"] for n in nodes}
    for n in nodes:
        parts = n["name"].split(".")
        k = len(parts) - 1
        while k > 0 and ".".join(parts[:k]) in prefix_is_symbol: k -= 1
        if k > 0: known_files.add("/".join(parts[:k]) + ".py")
    docs = collections.defaultdict(str)
    for n in nodes:
        f = to_file(n["name"])
        if TEST_RX.search(f): continue
        docs[f] += "\n" + n["name"] + "\n" + (n.get("text") or "")
    gold_in = [g for g in gold if g in docs or g.replace("/__init__.py", ".py") in docs]
    covered = bool(gold_in)
    goldset = set(gold) | {g.replace("/__init__.py", ".py") for g in gold}
    issue = task["problem_statement"]; ids = identifiers(issue)
    # A: identifier grep with idf
    df = collections.Counter(); hits = {}
    for f, txt in docs.items():
        hs = [i for i in ids if re.search(r"\b" + re.escape(i) + r"\b", txt)]
        hits[f] = hs
        for i in hs: df[i] += 1
    N = max(1, len(docs))
    A = {f: sum(math.log(1 + N / df[i]) for i in hs) for f, hs in hits.items() if hs}
    # also path-name match bonus
    for f in docs:
        base = Path(f).stem
        if len(base) > 3 and re.search(r"\b" + re.escape(base) + r"\b", issue): A[f] = A.get(f, 0) + 2 * math.log(1 + N)
    # B: BM25
    q = tok(issue); dtoks = {f: tok(t) for f, t in docs.items()}
    avg = sum(len(v) for v in dtoks.values()) / N
    dfb = collections.Counter(w for v in dtoks.values() for w in set(v))
    B = {}
    for f, v in dtoks.items():
        tf = collections.Counter(v); s = 0
        for w in set(q):
            if w in tf:
                idf = math.log(1 + (N - dfb[w] + .5) / (dfb[w] + .5))
                s += idf * tf[w] * 2.2 / (tf[w] + 1.2 * (.25 + .75 * len(v) / avg))
        if s: B[f] = s
    # C: harness graph similarity search on issue identifiers (what search_similar_code does)
    C = collections.defaultdict(float); short = task["repo"].split("/")[-1]
    for i in ids[:6]:
        t0 = time.time(); graph_q += 1
        try:
            sim = sg.get_similar_nodes(node=i, repo_name=task["repo"], k=10, use_local_storage=True,
                                       graph_dir=str(data / "graphs"), embeddings_dir=str(data / "embeddings"), base_commit=task["base_commit"])
        except Exception:
            sim = []
        t_graph.append(time.time() - t0)
        if not sim: empty_graph += 1
        for r, item in enumerate(sim):
            f = to_file(item["node_name"])
            if not TEST_RX.search(f): C[f] += 1.0 / (r + 1)
    def rrf(*ranks):
        s = collections.defaultdict(float)
        for rk in ranks:
            for r, f in enumerate(rk): s[f] += 1 / (20 + r)
        return rank_files(s)
    ranks = dict(grep_ids=rank_files(A), bm25=rank_files(B), graph_similar=rank_files(C))
    ranks["hybrid_grep_bm25"] = rrf(ranks["grep_ids"], ranks["bm25"])
    ranks["hybrid_all"] = rrf(ranks["grep_ids"], ranks["bm25"], ranks["graph_similar"])
    row = dict(instance_id=task["instance_id"], repo=task["repo"], n_gold=len(gold), gold_in_corpus=covered, n_files=N, n_ids=len(ids))
    for name, rk in ranks.items():
        pos = [rk.index(g) for g in goldset if g in rk]
        first = min(pos) if pos else None
        row[name] = first
        for k in (1, 3, 5, 10):
            agg[name][f"hit@{k}"].append(1 if first is not None and first < k else 0)
            agg[name][f"all_gold@{k}"].append(1 if len({g for g in gold if (g in rk[:k] or g.replace('/__init__.py', '.py') in rk[:k])}) == len(gold) else 0)
        agg[name]["mrr"].append(1 / (first + 1) if first is not None else 0)
    res.append(row)

summary = {name: {m: round(sum(v) / len(v), 3) for m, v in ms.items()} for name, ms in agg.items()}
meta = dict(tasks_evaluated=len(res), gold_file_present_in_graph_corpus=sum(r["gold_in_corpus"] for r in res),
            graph_queries=graph_q, graph_empty_results=empty_graph, graph_query_seconds_median=sorted(t_graph)[len(t_graph) // 2] if t_graph else None)
out.write_text(json.dumps(dict(meta=meta, summary=summary, rows=res), indent=1))
print(json.dumps(meta)); [print(k, v) for k, v in summary.items()]
