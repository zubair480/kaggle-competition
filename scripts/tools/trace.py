import json,re,sys
t="".join(x.get("data","") for x in json.load(open(sys.argv[1])))
for i in sys.argv[2:]:
    m=re.search(rf"TRACE_BEGIN {i}\n(.*?)TRACE_END {i}",t,re.S)
    print("=====",i); print("\n".join(l[:int(200)] for l in m.group(1).splitlines()) if m else "none")
