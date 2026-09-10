# -*- coding: utf-8 -*-
import json, re, io, os, urllib.request, collections, random
import pandas as pd
from PIL import Image
import sys; K=sys.argv[1]; P="Item Type Metadata:"; D="Dublin Core:"
REPO="/Users/daejinan/claude/ecoarchive-impact2026"; IMG=REPO+"/games/img"
random.seed(7)
df=pd.read_pickle("out/df.pkl"); ph=df[df.type=="기록-작품사진"].copy()
raw={}
for l in open("full/items.jsonl",encoding="utf-8"):
    r=json.loads(l)
    if r["item_type"]=="기록-작품사진": raw[r["id"]]=r
T=json.load(open(REPO+"/data/holdings/timeline.json",encoding="utf-8"))
CARDS=json.load(open(REPO+"/data/holdings/cards.json",encoding="utf-8"))
EV_TERMS={e["title"]:e["terms"] for e in T["events"]}
ORGS=[c["front"] for c in CARDS if c["type"]=="org"]
def norm(s): return re.sub(r'[\[\]\s()]','',s)
STOP=set(["사진","환경","작품","풍경","일상","사회","기록","자연"])
def g(i,k): return raw[i]["el"].get(P+k,[""])[0]
rows=[]
for r in ph.itertuples():
    i=r.id; artist=g(i,"Originator").strip(); title=raw[i]["el"].get(D+"Title",[""])[0]
    if not artist or not r.regions: continue
    kws=[k for k in r.kws if k not in STOP and not re.search(r'\d',k) and len(k)<=8 and k!=artist and not any(x in k for x in r.regions)]
    ev=next((t for t,terms in EV_TERMS.items() if any(any(term in k for term in terms) for k in r.kws) or any(term in title for term in terms)),None)
    org=next((o for o in ORGS if any(norm(o) in norm(k) for k in r.kws)),None)
    rows.append({"id":int(i),"title":title[:40],"artist":artist,"year":int(r.year) if r.year==r.year else None,"region":sorted(r.regions)[0],"keywords":kws[:4],"event":ev,"org":org,"lic":r.lic,"loc":r.filming[:30]})
print("후보:",len(rows),"| 사건 매칭:",sum(1 for x in rows if x["event"]),"| 단체 매칭:",sum(1 for x in rows if x["org"]),"| 키워드 있음:",sum(1 for x in rows if x["keywords"]))
# selection: prioritize event/org matches, then diversity by artist (max 5 each), total ~180
random.shuffle(rows); rows.sort(key=lambda x:-(bool(x["event"])*2+bool(x["org"])+bool(x["keywords"])*0.5))
sel=[]; per=collections.Counter()
for x in rows:
    if per[x["artist"]]>=5: continue
    if not x["keywords"] and not x["event"] and not x["org"]: continue
    sel.append(x); per[x["artist"]]+=1
    if len(sel)>=180: break
print("선정:",len(sel),"| 작가 수:",len(per),"| 사건:",sum(1 for x in sel if x["event"]),"| 단체:",sum(1 for x in sel if x["org"]))
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Referer":"https://archivelabedu.github.io/"})
    with urllib.request.urlopen(req,timeout=40) as r: return r.read()
out=[]
for x in sel:
    p=f"{IMG}/ph_{x['id']}.jpg"
    if not os.path.exists(p):
        try:
            files=json.loads(fetch(f"https://ecoarchive.org/api/files?key={K}&item={x['id']}"))
            fu=next((f["file_urls"] for f in files if f.get("mime_type","").startswith("image")),None)
            if not fu: continue
            im=Image.open(io.BytesIO(fetch(fu.get("square_thumbnail") or fu["fullsize"]))).convert("RGB"); im.thumbnail((420,420)); im.save(p,"JPEG",quality=78)
        except Exception as e: print("fail",x["id"],e); continue
    x["image"]=f"img/ph_{x['id']}.jpg"; x["url"]=f"https://ecoarchive.org/items/show/{x['id']}"; out.append(x)
json.dump(out,open(REPO+"/data/holdings/photo_cards.json","w",encoding="utf-8"),ensure_ascii=False)
print("저장:",len(out),"| 이미지 폴더 MB:",round(sum(os.path.getsize(IMG+"/"+f) for f in os.listdir(IMG))/1e6,1))
print("연대:",collections.Counter((x["year"]//10*10) for x in out if x["year"]).most_common(), "| 지역:",collections.Counter(x["region"] for x in out).most_common(8))
