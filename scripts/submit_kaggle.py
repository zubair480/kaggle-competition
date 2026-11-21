"""Submit submission.zip to the competition, or show submission status (auth is supplied by the environment).
usage: submit_kaggle.py status | submit "description" """
import json, os, subprocess, sys, time
API, COMP, ZIP = "https://www.kaggle.com/api/v1", "gemma-4-developer-agent", "submission.zip"
def curl(*a): return subprocess.run(["curl", "-sS", "-m", "120", *a], capture_output=True, text=True).stdout
def status():
    subs = json.loads(curl(f"{API}/competitions/submissions/list/{COMP}"))
    for s in subs: print(s["ref"], s["date"], s.get("status"), "score:", s.get("publicScore"), s.get("description"), s.get("errorDescription"))
    return subs
if sys.argv[1] == "status": status()
else:
    if any(s.get("status") == "pending" for s in status()): sys.exit("a submission is still pending; not submitting")
    d = json.loads(curl("-X", "POST", f"{API}/competitions/{COMP}/submissions/url/{os.path.getsize(ZIP)}/{int(time.time())}", "--form-string", f"fileName={ZIP}"))
    up = curl("-X", "PUT", "-H", "Content-Type: application/zip", "--data-binary", f"@{ZIP}", d["createUrl"], "-w", "\nHTTP %{http_code}")
    assert up.strip().endswith("HTTP 200"), up[-300:]
    print(curl("-X", "POST", f"{API}/competitions/submissions/submit/{COMP}", "--form-string", f"blobFileTokens={d['token']}", "--form-string", f"submissionDescription={sys.argv[2]}")[:300])
