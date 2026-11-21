# Retrieval research

## Question

How should the agent find the file to edit, given about 40 tool calls and a 32k context? Specifically: are the
three code-graph tools (`search_similar_code`, `get_code_neighbors`, `get_code_subgraph`) worth calls?

## Experiment R1: model-free localization benchmark (measured)

Script: `scripts/localization_benchmark.py`. Results: `experiments/retrieval/localization_results.json`.

- **Tasks:** all 129 public tasks.
- **Corpus:** every function and class in the official pre-computed code graph for the task's commit, grouped
  into files; test files excluded.
- **Gold:** non-test `.py` files touched by the reference patch (offline use only).
- **Query:** the issue text, or identifiers extracted from it (backticked names, CamelCase, snake_case, dotted
  paths).
- **Graph strategy:** calls `swegemma.graph.get_similar_nodes`, the exact backend of the `search_similar_code`
  tool, once per identifier (up to 6), and merges the returned nodes into files.

| Strategy | hit@1 | hit@3 | hit@5 | hit@10 | all gold files in top 5 | MRR |
|---|---|---|---|---|---|---|
| Identifier grep, idf-weighted | 0.264 | 0.426 | 0.473 | 0.543 | 0.341 | 0.357 |
| BM25 on the whole issue | 0.194 | 0.426 | 0.535 | 0.628 | 0.395 | 0.345 |
| Graph similarity (the harness tool) | 0.225 | 0.326 | 0.349 | 0.372 | 0.233 | 0.275 |
| Grep + BM25 (rank fusion) | 0.287 | 0.481 | 0.535 | 0.651 | 0.372 | 0.409 |
| Grep + BM25 + graph (rank fusion) | 0.279 | 0.488 | 0.589 | 0.651 | 0.411 | 0.408 |

hit@k = at least one gold file in the top k. Denominator is all 129 tasks.

Other measurements from the same run:

- **Graph coverage ceiling:** a gold file is present in the graph corpus for only 109 of 129 tasks (84%). The
  rest are new files, scripts, or files with no indexed function. No retrieval over the graph can find those.
- **Empty results:** 69 of 458 graph similarity queries (15%) returned nothing, because the query must resolve
  to an existing node name.
- **Latency:** median 0.06 s per graph query once loaded, so cost is the tool call, not compute.

## Reading the result

1. The graph similarity tool is the weakest single strategy at every k above 1 and adds nothing to hit@1 or
   hit@10 when fused with lexical search. It gains 5 points at hit@5 only.
2. Plain lexical search gets a gold file into the top 5 for roughly half of the tasks. The other half need the
   agent to read code and follow references, which is what a `grep`-then-read loop does.
3. This agrees with independent community evidence: a 129-task ablation (thread 746250) found adding the graph
   tools lowered the resolved count (50 vs 55, single runs) and that semantic searches returned empty results;
   repo B's author measured that quoting the glob in `git grep -- '*.py'` moved gold-file hit@5 from 1/9 to 4/9.

Limits of R1: the file mapping from graph node names is heuristic; the benchmark measures file-level
localization, not line-level; and it does not measure what the model does with the results.

## Decision

- **Do not declare the graph tools.** When they are not declared the harness also omits the "Code Intelligence
  Tools" section from the task prompt, which saves context and removes a distraction.
- **Search lexically, with several identifiers at once,** using `git grep -n -E "a|b|c" -- '*.py'` (quoted glob),
  filtered to exclude tests, capped with `head`.
- **Read narrowly** around hits with line ranges.

## Not done

Line-level localization, agentic retrieval measured end to end, and symbol-importance ranking were not
evaluated: each needs model runs on GPU, and the available GPU budget went to the end-to-end agent evaluation.
