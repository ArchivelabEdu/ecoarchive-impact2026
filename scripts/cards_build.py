# -*- coding: utf-8 -*-
import json, re, io, os, urllib.request, collections
from PIL import Image
import sys; K=sys.argv[1]; P="Item Type Metadata:"; D="Dublin Core:"
REPO="/Users/daejinan/claude/ecoarchive-impact2026"; IMG=REPO+"/games/img"; os.makedirs(IMG,exist_ok=True)
T=json.load(open(REPO+"/data/holdings/timeline.json",encoding="utf-8"))
COLS=json.load(open(REPO+"/data/holdings/collections.json",encoding="utf-8"))
INTRO=json.load(open(REPO+"/content/collections_intro.json",encoding="utf-8"))
raw={}
for l in open("full/items.jsonl",encoding="utf-8"):
    r=json.loads(l)
    if r["item_type"] in ("정보사전-사진작가",): raw[r["id"]]=r
def fetch(url,timeout=40):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Referer":"https://archivelabedu.github.io/"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return r.read()
def save_img(url,name,size=420):
    p=f"{IMG}/{name}.jpg"
    if os.path.exists(p): return f"img/{name}.jpg"
    try:
        im=Image.open(io.BytesIO(fetch(url))).convert("RGB"); im.thumbnail((size,size)); im.save(p,"JPEG",quality=82); return f"img/{name}.jpg"
    except Exception as e: print("img fail",name,e); return None
cards=[]
# ---- events (47)
for e in T["events"]:
    img=None
    try:
        files=json.loads(fetch(f"https://ecoarchive.org/api/files?key={K}&item={e['id']}"))
        fu=next((f["file_urls"] for f in files if f.get("mime_type","").startswith("image")),None)
        if fu: img=save_img(fu.get("square_thumbnail") or fu["fullsize"],f"ev_{e['id']}")
    except Exception as ex: print("files fail",e["id"],ex)
    cards.append({"type":"event","id":e["id"],"front":e["title"],"year":int(e["start"]) if e["start"].isdigit() else None,"end":e["end"],"subject":e["subject"],
        "back":e["desc"],"count":e["n"],"colls":[c["k"] for c in e["colls"]],"url":e["url"],"image":img})
# ---- artists (profile photo)
for i,r in raw.items():
    e=r["el"]; g=lambda k: e.get(P+k,[""])[0]
    m=re.search(r'src="([^"]+)"',g("Artist Photo Profile")); img=save_img(m.group(1).replace("http://","https://"),f"ar_{i}") if m else None
    works=[g(f"Selected Works {n}") for n in range(1,6) if g(f"Selected Works {n}")]
    career=[x.strip() for x in g("Career").split("\n") if x.strip()][:2]
    hints=[h for h in [("대표 작업: "+", ".join(works[:3])) if works else "", ("경력: "+career[0]) if career else "", ("수상·선정: "+g("Award Selection Experience").split("\n")[0]) if g("Award Selection Experience") else "", "환경사진아카이브 참여 작가"] if h]
    cards.append({"type":"person","id":i,"front":g("Artist Name") or e.get(D+"Title",[""])[0],"role":"사진작가","hints":hints[:4],"back":g("Introduction")[:200] or (career[0] if career else ""),"url":f"https://ecoarchive.org/items/show/{i}","image":img})
# ---- persons (개인 컬렉션 8)
for c in COLS:
    if c["kind"]!="개인": continue
    who=INTRO.get(c["name"],{}).get("who","")
    hints=[f"기증 기록 {c['total']:,}건, {c['year_min']}–{c['year_max']}", "특징 키워드: "+", ".join(k["k"] for k in c["distinct_kw"][:3]) if c["distinct_kw"] else "주제: "+(c["subject"][0]["k"] if c["subject"] else ""), who.split(". ")[0][:60]+"…" if who else "", "풀숲 개인 컬렉션 기증자"]
    cards.append({"type":"person","id":c["id"],"front":c["name"],"role":"기증자","hints":[h for h in hints if h][:4],"back":who,"url":c["url"],"image":None})
# ---- orgs (top 40 with founded)
byname={c["name"]:c for c in COLS}
orgs=[o for o in T["orgs"] if o["founded"] and o["n_rec"]>0]; orgs.sort(key=lambda o:-o["n_rec"])
for o in orgs[:40]:
    cc=byname.get(o["name"]); kw=[k["k"] for k in cc["distinct_kw"][:4]] if cc else []
    cards.append({"type":"org","id":o["id"],"front":o["name"],"year":o["founded"],"areas":o["areas"],"count":o["n_rec"],"back":o["desc"] or (INTRO.get(o["name"],{}).get("who","")),
        "hints":[h for h in ["활동영역: "+", ".join(o["areas"]) if o["areas"] else "", "특징 키워드: "+", ".join(kw) if kw else "", f"관련 기록 {o['n_rec']:,}건", f"설립 {o['founded']}년"] if h],"url":o["url"],"image":None})
# ---- collections (34)
for c in COLS:
    cards.append({"type":"collection","id":c["id"],"front":c["name"],"kind":c["kind"],"keywords":[k["k"] for k in c["distinct_kw"][:6]] or [k["k"] for k in c["top_kw"][:6]],"count":c["total"],"year":c["year_min"],"back":INTRO.get(c["name"],{}).get("who",""),"url":c["url"]})
# ---- years
for y in T["years"]:
    cards.append({"type":"year","front":str(y),"year":y,"count":T["rec_by_year"].get(str(y),0),"keywords":T["year_distinct"].get(str(y),[]),"top":T["year_top"].get(str(y),[]),
        "events":[e["title"] for e in T["events"] if e["start"]==str(y)],"orgs":[o["name"] for o in T["orgs"] if o["founded"]==y][:5],"chron":T["chron_by_year"].get(str(y),0)})
json.dump(cards,open(REPO+"/data/holdings/cards.json","w",encoding="utf-8"),ensure_ascii=False)
print(collections.Counter(c["type"] for c in cards), "| images:",sum(1 for c in cards if c.get("image")), "| size KB:",os.path.getsize(REPO+"/data/holdings/cards.json")//1024)
