"""usage: python3 -I pull_kernel.py owner/slug outdir  -> saves notebook source + metadata"""
import json, subprocess, sys, os
ref, out = sys.argv[1], sys.argv[2]
o, s = ref.split("/")
r = subprocess.run(["curl", "-sS", "-m", "90", f"https://www.kaggle.com/api/v1/kernels/pull?userName={o}&kernelSlug={s}"], capture_output=True, text=True).stdout
d = json.loads(r)
os.makedirs(out, exist_ok=True)
json.dump(d.get("metadata", {}), open(os.path.join(out, f"{o}__{s}.meta.json"), "w"), indent=1)
src = d.get("blob", {}).get("source", "")
ext = ".ipynb" if src.lstrip().startswith("{") else ".py"
open(os.path.join(out, f"{o}__{s}{ext}"), "w").write(src)
if ext == ".ipynb":
    nb = json.loads(src)
    with open(os.path.join(out, f"{o}__{s}.txt"), "w") as f:
        for c in nb.get("cells", []):
            f.write(f"\n##### [{c['cell_type']}]\n" + "".join(c["source"]) + "\n")
print(ref, len(src))
