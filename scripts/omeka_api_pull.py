import json, time, urllib.request, urllib.parse, concurrent.futures, os, threading
import sys; K=sys.argv[1]; BASE="https://ecoarchive.org/api"
LAST=2223
lock=threading.Lock(); out=open("full/items.jsonl","a",encoding="utf-8"); log=open("full/pull.log","a")
def get(url,tries=4):
    for t in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"pulsoop-impact/1.0"}),timeout=120) as r:
                return json.load(r)
        except Exception as e:
            err=e; time.sleep(2*(t+1))
    raise err
def flat(it):
    el={}
    for e in it.get("element_texts",[]):
        n=e["element"]["name"]; s=e["element_set"]["name"]
        el.setdefault(f"{s}:{n}",[]).append(e["text"])
    return {"id":it["id"],"public":it.get("public"),"featured":it.get("featured"),"added":it.get("added"),"modified":it.get("modified"),
            "item_type":(it.get("item_type") or {}).get("name"),"item_type_id":(it.get("item_type") or {}).get("id"),
            "collection_id":(it.get("collection") or {}).get("id"),"files":(it.get("files") or {}).get("count"),
            "tags":[t["name"] for t in it.get("tags",[])],"el":el}
def page(p):
    if os.path.exists(f"full/done_{p}"): return
    d=get(f"{BASE}/items?key={K}&per_page=50&page={p}")
    rows=[json.dumps(flat(it),ensure_ascii=False) for it in d]
    with lock:
        out.write("\n".join(rows)+"\n"); out.flush(); log.write(f"{p}\t{len(d)}\n"); log.flush()
    open(f"full/done_{p}","w").close()
with concurrent.futures.ThreadPoolExecutor(4) as ex:
    list(ex.map(page,range(1,LAST+1)))
print("done")
