"""Push / poll / fetch a private Kaggle notebook through the REST API (auth is supplied by the environment).
usage: kaggle_kernel.py push NOTEBOOK.ipynb slug "Title" | status slug | output slug DEST_DIR"""
import json, subprocess, sys, os, urllib.parse
API = "https://www.kaggle.com/api/v1"
def curl(*args):
    return subprocess.run(["curl", "-sS", "-m", "300", *args], capture_output=True, text=True).stdout
USER = json.loads(curl(f"{API}/hello"))["userName"]
cmd = sys.argv[1]
if cmd == "push":
    nb, slug, title = sys.argv[2:5]
    body = dict(slug=f"{USER}/{slug}", newTitle=title, text=open(nb).read(), language="python", kernelType="notebook",
                isPrivate=True, enableGpu=(os.environ.get("KK_GPU","1")=="1"), enableInternet=False, machineShape=("NvidiaL4" if os.environ.get("KK_GPU","1")=="1" else "None"),
                competitionDataSources=["gemma-4-developer-agent"],
                datasetDataSources=["metric/gemma-4-developer-agent-wheelhouse"],
                modelDataSources=[f"google/gemma-4/Other/gemma-4-{m}-it-qat-w4a16-ct/2" for m in ("31b", "12b", "e2b", "e4b")],
                kernelDataSources=[], categoryIds=[],
                # same pinned image as the official starter notebook (Python 3.12; the wheelhouse is cp312)
                dockerImage="gcr.io/kaggle-private-byod/python@sha256:37c64f7dd9c54116ecd1bcc88817c5469b88387388fade02bfa8bf3fc647d461",
                dockerImagePinningType="original")
    open("/tmp/_push.json", "w").write(json.dumps(body))
    print(curl("-X", "POST", "-H", "Content-Type: application/json", "--data-binary", "@/tmp/_push.json", f"{API}/kernels/push")[:800])
elif cmd == "status":
    print(curl(f"{API}/kernels/status?userName={USER}&kernelSlug={sys.argv[2]}")[:600])
elif cmd == "output":
    slug, dest = sys.argv[2:4]; os.makedirs(dest, exist_ok=True); tok = ""
    while True:
        d = json.loads(curl(f"{API}/kernels/output?userName={USER}&kernelSlug={slug}&pageSize=100" + (f"&pageToken={urllib.parse.quote(tok)}" if tok else "")))
        for f in d.get("files", []):
            p = os.path.join(dest, f["fileName"]); os.makedirs(os.path.dirname(p), exist_ok=True)
            subprocess.run(["curl", "-sSL", "-m", "600", "-o", p, f["url"]])
        if d.get("log"): open(os.path.join(dest, "_log.json"), "w").write(d["log"])
        tok = d.get("nextPageToken") or ""
        if not tok: break
    print(sorted(os.listdir(dest))[:40])
