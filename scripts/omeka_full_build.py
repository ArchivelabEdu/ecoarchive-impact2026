# -*- coding: utf-8 -*-
import json,re,collections,math,sys,os
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"]="Apple SD Gothic Neo"; plt.rcParams["axes.unicode_minus"]=False
plt.rcParams["figure.dpi"]=150
C=collections.Counter; P="Item Type Metadata:"; D="Dublin Core:"
colls={c["id"]:[e["text"] for e in c.get("element_texts",[]) if e["element"]["name"]=="Title"][0] for c in json.load(open("full/collections.json"))}
PERSON={22,23,24,25,26,27,28,54}
rows=[json.loads(l) for l in open("full/items.jsonl",encoding="utf-8")]
seen=set(); rows=[r for r in rows if not (r["id"] in seen or seen.add(r["id"]))]
print("items:",len(rows))
def g(r,k,default=""):
    v=r["el"].get(k); return v[0] if v else default
def gl(r,k):
    out=[]
    for v in r["el"].get(k,[]): out+= [x.strip() for x in re.split(r'[;,]',v) if x.strip()] if k.endswith("Keyword") or k.endswith("Relation") else [v.strip()]
    return out
def year(r):
    for k in [P+"Year of Creation",P+"Date of Creation",D+"Date",P+"Chronological Year",P+"Case Start Date"]:
        m=re.match(r'(\d{4})',g(r,k))
        if m:
            y=int(m.group(1))
            if 1900<=y<=2026: return y
    return None
def kws(r):
    k=gl(r,P+"Keyword") or gl(r,D+"Relation")
    return list(dict.fromkeys(k+[t.strip() for t in r["tags"]]))
REG={"서울":"서울","서울특별시":"서울","서울시":"서울","부산":"부산","부산광역시":"부산","대구":"대구","대구광역시":"대구","인천":"인천","인천광역시":"인천","광주":"광주","광주광역시":"광주","대전":"대전","대전광역시":"대전","울산":"울산","울산광역시":"울산","세종":"세종","세종특별자치시":"세종","경기":"경기","경기도":"경기","강원":"강원","강원도":"강원","강원특별자치도":"강원","충북":"충북","충청북도":"충북","충남":"충남","충청남도":"충남","전북":"전북","전라북도":"전북","전북특별자치도":"전북","전남":"전남","전라남도":"전남","경북":"경북","경상북도":"경북","경남":"경남","경상남도":"경남","제주":"제주","제주도":"제주","제주특별자치도":"제주",
 "새만금":"전북","부안":"전북","매향리":"경기","시화호":"경기","팔당":"경기","대추리":"경기","평택":"경기","수원":"경기","안양":"경기","안산":"경기","성남":"경기","고양":"경기","용인":"경기","화성":"경기","온산":"울산","가리왕산":"강원","설악산":"강원","동강":"강원","삼척":"강원","영월":"강원","춘천":"강원","원주":"강원","영광":"전남","여수":"전남","순천":"전남","광양":"전남","고리":"부산","월성":"경북","울진":"경북","영덕":"경북","경주":"경북","포항":"경북","안동":"경북","밀양":"경남","창원":"경남","마산":"경남","진주":"경남","천성산":"경남","거제":"경남","통영":"경남","강정":"제주","서귀포":"제주","비자림":"제주","태안":"충남","안면도":"충남","가로림만":"충남","서산":"충남","당진":"충남","청주":"충북","충주":"충북","단양":"충북","북한산":"서울","한강":"서울","굴업도":"인천","강화":"인천","영종도":"인천","송도":"인천","전주":"전북","군산":"전북","익산":"전북"}
def regions(r):
    s=set()
    for k in kws(r)+[g(r,P+"Filming Location")]:
        for tok in re.split(r'[\s,/·]+',k):
            tok=tok.strip("()[]")
            if tok in REG: s.add(REG[tok])
        if k in REG: s.add(REG[k])
    return s
recs=[]
for r in rows:
    it=r["item_type"] or ""
    y=year(r)
    recs.append({"id":r["id"],"public":r["public"],"type":it,"coll_id":r["collection_id"],"coll":colls.get(r["collection_id"],""),
        "rtype":g(r,P+"Type of Records"),"rform":g(r,P+"Format of Records"),"orig":g(r,P+"Format of Originals"),
        "subject":g(r,P+"Related Subject"),"year":y,"decade":(y//10*10 if y else None),
        "creator":"; ".join(r["el"].get(D+"Creator",[])),"files":r["files"] or 0,"preview":bool(g(r,P+"Preview")),
        "lang":g(r,P+"Language of Records"),"rights":g(r,P+"Rights") or g(r,D+"Rights"),"lic":g(r,P+"Copyright 2. License"),
        "desc":len(g(r,D+"Description")),"nkw":len(kws(r)),"added":r["added"][:7],"descdate":g(r,P+"Description Date")[:4],
        "descriptor":g(r,P+"Descriptor"),"pages":(int(m.group(1)) if (m:=re.search(r'(\d[\d,]*)\s*쪽'," ".join(r["el"].get(P+"Size/Quantity",[])).replace(",",""))) else None),
        "rel":any(g(r,P+k) for k in ["Related Record","Related Case","Related Chronology","Related Organization"]),
        "regions":regions(r),"kws":kws(r),"filming":g(r,P+"Filming Location"),"vis":g(r,P+"Visibility")})
df=pd.DataFrame(recs)
df.to_pickle("out/df.pkl")
print(df.type.value_counts()); print("public:",df.public.value_counts().to_dict())
