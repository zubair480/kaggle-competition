"""usage: python3 -I dl_comp.py <dest_dir> <prefix_or_regex> [max_files]  - mirrors matching competition files"""
import json, subprocess, urllib.parse, os, re, sys
from concurrent.futures import ThreadPoolExecutor
dest, pat = sys.argv[1], re.compile(sys.argv[2]); mx = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
fl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dl", "filelist.json")
files = [f for f in json.load(open(fl)) if pat.search(f["name"])][:mx]
def get(f):
    n = f["name"]; p = os.path.join(dest, n)
    if os.path.exists(p) and os.path.getsize(p) == f["totalBytes"]: return "have"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    for _ in range(4):
        subprocess.run(["curl", "-sSL", "-m", "900", "-o", p, "https://www.kaggle.com/api/v1/competitions/data/download/gemma-4-developer-agent/" + urllib.parse.quote(n, safe="")])
        if os.path.exists(p) and os.path.getsize(p) == f["totalBytes"]: return "ok"
    return "FAIL " + n
with ThreadPoolExecutor(6) as ex: res = list(ex.map(get, files))
print(len(files), {r.split()[0]: sum(1 for x in res if x.split()[0] == r.split()[0]) for r in res}, [r for r in res if r.startswith("FAIL")][:5])
