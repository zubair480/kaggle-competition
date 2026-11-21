"""Offline failure classification of an evaluation run against the reference patches.
usage: classify_failures.py LOG.json TASKS.jsonl RESULTS.jsonl OUT.csv   (reference patches are read here only)"""
import json, re, csv, collections, sys
log, tasks_p, res_p, out = sys.argv[1:5]
t = "".join(x.get("data", "") for x in json.load(open(log)))
tasks = {json.loads(l)["instance_id"]: json.loads(l) for l in open(tasks_p)}
files = lambda p: set(re.findall(r"^\+\+\+ b/(\S+)", p or "", re.M))
istest = lambda f: bool(re.search(r"(^|/)tests?/|test_[^/]*\.py$|_test\.py$", f))
timed = set(re.findall(r"Task (\S+) agent timed out", t))
rows, cnt = [], collections.Counter()
for l in open(res_p):
    r = json.loads(l); i = r["id"]
    m = re.search(rf"PATCH_BEGIN {i}\n(.*?)PATCH_END {i}", t, re.S); ap = m.group(1) if m else ""
    gold = {f for f in files(tasks[i]["patch"]) if not istest(f)}; got = files(ap)
    if r["resolved"]: cat = "resolved"
    elif r["patch"] == 0: cat = "no_edit_calls_exhausted" if r["calls"] >= 30 else ("no_edit_timeout" if i in timed else "no_edit_gave_up")
    elif not (gold & got): cat = "wrong_file"
    elif gold - got: cat = "missed_some_files"
    else: cat = "right_files_wrong_fix"
    cnt[cat] += 1
    rows.append(dict(task=i, resolved=r["resolved"], category=cat, tool_calls=r["calls"], duration_s=r["dur"], patch_chars=r["patch"],
                     timed_out=i in timed, gold_src_files=len(gold), gold_files_touched=len(gold & got), agent_files=len(got),
                     gold_changed_lines=len(re.findall(r"^[+-](?![+-])", tasks[i]["patch"], re.M)), exit_code=r["exit"]))
w = csv.DictWriter(open(out, "w", newline=""), fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(dict(cnt)); print("timed out:", sum(r["timed_out"] for r in rows), "| timed out and resolved:", sum(r["timed_out"] and r["resolved"] for r in rows))
for c in cnt: print(c, "median gold lines", sorted(r["gold_changed_lines"] for r in rows if r["category"] == c)[cnt[c] // 2])
