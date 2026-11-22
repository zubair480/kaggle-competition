import json,re,sys,statistics as st
log=json.load(open(sys.argv[1])); text="".join(x.get("data","") for x in log) if isinstance(log,list) else str(log)
sound=set(open("data/sound_tasks.txt").read().split())
rows=[];cur=None
for line in text.splitlines():
    m=re.search(r"\[(\d+)/(\d+)\] Evaluating (\S+)",line)
    if m: cur=m.group(3)
    m=re.search(r"resolved=(\w+), exit_code=(\S+), patch_chars=(\d+), tool_calls=(\d+), duration=([\d.]+)s",line)
    if m and cur:
        rows.append(dict(id=cur,resolved=m.group(1)=="True",exit=m.group(2),patch=int(m.group(3)),calls=int(m.group(4)),dur=float(m.group(5)),sound=cur in sound));cur=None
if len(sys.argv)>2: open(sys.argv[2],"w").write("\n".join(json.dumps(r) for r in rows)+"\n")
d=[r["dur"] for r in rows]; s=[r for r in rows if r["sound"]]
print(f"n={len(rows)} resolved={sum(r['resolved'] for r in rows)} | sound n={len(s)} resolved={sum(r['resolved'] for r in s)}")
if d: print(f"dur mean={st.mean(d):.0f}s median={st.median(d):.0f} p90={sorted(d)[int(.9*len(d))-1]:.0f} max={max(d):.0f} total={sum(d)/60:.1f}min; calls mean={st.mean(r['calls'] for r in rows):.1f}; empty patches={sum(r['patch']==0 for r in rows)}")
for r in rows: print(f"{r['id']:16} {'S' if r['sound'] else '-'} {'PASS' if r['resolved'] else 'fail'} calls={r['calls']:3} dur={r['dur']:5.0f} patch={r['patch']}")
