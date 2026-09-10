# -*- coding: utf-8 -*-
import json,re,collections,math,itertools
import pandas as pd, numpy as np
C=collections.Counter; P="Item Type Metadata:"; D="Dublin Core:"
import os; OUT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"data","holdings")+"/"
df=pd.read_pickle("out/df.pkl")
raw={}
for l in open("full/items.jsonl",encoding="utf-8"):
    r=json.loads(l); raw[r["id"]]=r
colls_raw={c["id"]:c for c in json.load(open("full/collections.json"))}
def ctext(c,name):
    v=[e["text"] for e in c.get("element_texts",[]) if e["element"]["name"]==name]; return v[0] if v else ""
def norm(s): return re.sub(r'[\[\]\s]','',s)
PERSON={"구도완","김현구","장재연","이상돈","김호철","서진옥","윤제용","정태석"}
STOPK=set(["사회","환경","기록","일반","환경운동","환경단체","정치","경제","문화","과학","사진","국제","노동","교육","생활","스포츠","종교","연예","지역","칼럼","기사","기타"])|set(norm(c) for c in df.coll.unique() if c)|set(df.coll.unique())
def dump(name,obj): json.dump(obj,open(OUT+name,"w",encoding="utf-8"),ensure_ascii=False)
def cnt(s,k=None):
    v=s.value_counts(); v=v[v.index!=""]; 
    return [{"k":str(a),"v":int(b)} for a,b in (v.head(k) if k else v).items()]
gen=df[(df.type=="기록-일반")&df.public]; rec=df[df.type.str.startswith("기록")&df.public]; photo=df[df.type=="기록-작품사진"]
allc=df[df.coll!=""]
# ---- summary
yy=gen.year.dropna()
summary={"items":int(len(df)),"public":int(df.public.sum()),"gen":int((df.type=="기록-일반").sum()),"gen_public":int(len(gen)),"photo":int(len(photo)),
 "chron":int((df.type=="정보사전-연표").sum()),"org":int((df.type=="정보사전-조직").sum()),"event":int((df.type=="정보사전-사건").sum()),"artist":int((df.type=="정보사전-사진작가").sum()),
 "collections":int(allc.coll.nunique()),"orgs":int(sum(1 for c in allc.coll.unique() if c not in PERSON)),"persons":int(sum(1 for c in allc.coll.unique() if c in PERSON)),
 "file_rate":round(float((gen.files>0).mean()),4),"access_rate":round(float(((gen.files>0)|gen.preview).mean()),4),"pages_sum":int(gen.pages.sum()),"pages_n":int(gen.pages.notna().sum()),
 "year_min":int(yy.min()),"year_max":int(yy.max()),"year_median":int(yy.median()),"year_rate":round(float(gen.year.notna().mean()),4),
 "keywords_unique":int(len(set(k for ks in gen.kws for k in ks))),"kw_rate":round(float((gen.nkw>0).mean()),4),"kw_mean":round(float(gen.nkw.mean()),2),
 "subject_rate":round(float((gen.subject!="").mean()),4),"rel_rate":round(float(gen.rel.mean()),4),"rights_rate":round(float((gen.rights!="").mean()),4),
 "external_rate":None,"snapshot":"2026-09-10"}
cr=gen[gen.creator.ne("")&gen.creator.ne("미상")]
ext=cr[[norm(a.split(';')[0])!=norm(b) for a,b in zip(cr.creator,cr.coll)]]
summary["external_rate"]=round(len(ext)/len(cr),4); summary["creators_unique"]=int(cr.creator.nunique()); summary["external_n"]=int(len(ext)); summary["creator_n"]=int(len(cr))
govpat=r'(부|처|청|원|시|도|군|구|위원회|공사|공단|국회|의원|연구원|진흥원)$'
gov=ext[ext.creator.str.split(';').str[0].str.strip().str.contains(govpat)&~ext.creator.str.contains('연합|연대|모임|센터|협의회|네트워크|시민|환경운동')]
summary["gov_n"]=int(len(gov))
adv=["보도자료","공문","포스터","성명서","유인물","요청서/질의문","촉구서","기자회견문","웹포스터","카드뉴스","통보문","의견서"]
summary["kw_excl_press"]=True; summary["adv_n"]=int(gen.rform.isin(adv).sum()); summary["policy_n"]=int(gen.rform.isin(["요청서/질의문","촉구서","성명서","기자회견문","의견서","탄원서","진정서"]).sum())
dump("summary.json",summary)
# ---- holdings
dump("holdings.json",{
 "type":cnt(df.type),"type_public":[{"k":t,"pub":int(g.public.sum()),"priv":int((~g.public).sum())} for t,g in df.groupby("type") if t],
 "rtype":cnt(gen.rtype),"rform":cnt(gen.rform,30),"orig":cnt(gen.orig,3),"lang":cnt(gen.lang,12),
 "file_by_type":[{"k":t,"v":round(float(((g.files>0)|g.preview).mean()),4),"n":int(len(g))} for t,g in gen.groupby("rtype") if t],
 "year":[{"k":int(y),"v":int(v)} for y,v in gen.year.value_counts().sort_index().items() if y>=1960],
 "year_by_coll":{c:[{"k":int(y),"v":int(v)} for y,v in g.year.value_counts().sort_index().items() if y>=1960] for c,g in gen.groupby("coll") if c},
 "decade":[{"k":f"{int(d)}s","v":int(v)} for d,v in gen.decade.value_counts().sort_index().items() if d>=1970],
 "subject":cnt(gen.subject),
 "subject_by_decade":[{"decade":f"{int(d)}s",**{s:int(v) for s,v in g.subject[g.subject!=""].value_counts().items()}} for d,g in gen.groupby("decade") if d>=1970],
 "pages_hist":[{"k":k,"v":int(v)} for k,v in pd.cut(gen.pages.dropna(),[0,1,2,4,10,30,100,300,1000,100000],labels=["1","2","3-4","5-10","11-30","31-100","101-300","301-1000","1000+"]).value_counts().sort_index().items()],
 "regions":[{"k":k,"v":int(v)} for k,v in C(x for s in gen.regions for x in s).most_common()],
 "regions_photo":[{"k":k,"v":int(v)} for k,v in C(x for s in photo.regions for x in s).most_common()],
 "region_rate":round(float((gen.regions.map(len)>0).mean()),4),
 "quality":{"제목":1.0,"생산자":round(float((gen.creator!="").mean()),4),"원문":summary["access_rate"],"키워드":summary["kw_rate"],"생산연도":summary["year_rate"],"설명":round(float((gen.desc>0).mean()),4),"주제":summary["subject_rate"],"연관":summary["rel_rate"],"권리":summary["rights_rate"]},
 "added_month":[{"k":k,"v":int(v)} for k,v in df.added.value_counts().sort_index().items() if k>="2019-01"],
 "added_year_type":[{"year":y,**{t:int(v) for t,v in g.type.value_counts().items() if t}} for y,g in df.groupby(df.added.str[:4])],
 "descdate":[{"k":k,"v":int(v)} for k,v in gen.descdate.value_counts().sort_index().items() if re.match(r'\d{4}$',k)],
 "adv":[{"k":k,"v":int(v)} for k,v in gen[gen.rform.isin(adv)].rform.value_counts().items()],
})
# ---- keywords
allk=C(k for ks in gen.kws for k in ks); N=len(gen)
gk=gen[gen.year.notna()&(gen.coll!="한겨레")].copy(); gk["y"]=gk.year.astype(int)
def okk(k): return k not in STOPK and not re.search(r'\d',k) and len(k)<=10
# 5-year windows
wins=[(1980,1989)]+[(a,a+4) for a in range(1990,2025,5)]
win_top=[]
for a,b in wins:
    g=gk[(gk.y>=a)&(gk.y<=b)]; kc=C(k for ks in g.kws for k in ks if okk(k)); n=len(g)
    win_top.append({"win":f"{a}-{b}","n":int(n),"top":[{"k":k,"v":int(v),"share":round(v/n,4)} for k,v in kc.most_common(40)],
        "distinct":[{"k":k,"v":int(kc[k]),"score":round((kc[k]/n)/(allk[k]/N),2)} for k in sorted([k for k,v in kc.items() if v>=25],key=lambda k:-(kc[k]/n)/(allk[k]/N))[:25]]})
dump("keywords_windows.json",win_top)
# yearly series for top 400 keywords + lifecycle
topk=[k for k,_ in allk.most_common(800) if okk(k)][:400]
series={k:C() for k in topk}; life={}
for ks,y in zip(gk.kws,gk.y):
    for k in set(ks):
        if k in series: series[k][y]+=1
yearN=gk.y.value_counts().to_dict()
dump("keywords_series.json",{"years":sorted(int(y) for y in yearN if y>=1980),"yearN":{int(y):int(v) for y,v in yearN.items()},
 "series":{k:{int(y):int(v) for y,v in s.items() if y>=1980} for k,s in series.items()}})
# lifecycle first/last (min 20)
kw_years=collections.defaultdict(list)
for ks,y in zip(gk.kws,gk.y):
    for k in set(ks):
        if okk(k) and allk[k]>=20: kw_years[k].append(y)
life=[{"k":k,"n":int(allk[k]),"first":int(np.percentile(v,5)),"last":int(np.percentile(v,95)),"peak":int(C(v).most_common(1)[0][0]),"median":int(np.median(v))} for k,v in kw_years.items()]
life.sort(key=lambda x:-x["n"]); dump("keywords_life.json",life[:600])
# rising/falling between consecutive decades (min 30 in either)
dec={d:C(k for ks in g.kws for k in ks if okk(k)) for d,g in gk.groupby(gk.y//10*10) if d>=1990}
decN={d:len(g) for d,g in gk.groupby(gk.y//10*10) if d>=1990}
rf=[]
ds=sorted(dec)
for a,b in zip(ds,ds[1:]):
    for k in set(dec[a])|set(dec[b]):
        va,vb=dec[a][k],dec[b][k]
        if max(va,vb)<30: continue
        sa,sb=(va+5)/decN[a],(vb+5)/decN[b]   # additive smoothing so brand-new terms rank by magnitude, not tie at the top
        rf.append({"from":f"{a}s","to":f"{b}s","k":k,"a":int(va),"b":int(vb),"ratio":round(math.log2(sb/sa),2)})
dump("keywords_change.json",rf)
# co-occurrence among top 150
top150=[k for k in topk[:150]]; idx=set(top150); co=C()
for ks in gen[gen.coll!='한겨레'].kws:
    s=sorted(set(k for k in ks if k in idx))
    for a,b in itertools.combinations(s,2): co[(a,b)]+=1
edges=[{"s":a,"t":b,"w":int(w)} for (a,b),w in co.most_common(600) if w>=8]
dump("keywords_cooc.json",{"nodes":[{"id":k,"n":int(allk[k])} for k in top150],"edges":edges})
# keyword dictionary (all with n>=3)
dic=[{"k":k,"n":int(v)} for k,v in allk.most_common() if v>=3]
kwcoll=collections.defaultdict(C); kwyr=collections.defaultdict(list)
for ks,c,y in zip(gen.kws,gen.coll,gen.year):
    for k in set(ks):
        if allk[k]>=3:
            kwcoll[k][c]+=1
            if y==y: kwyr[k].append(int(y))
for d in dic:
    k=d["k"]; d["coll"]=kwcoll[k].most_common(1)[0][0] if kwcoll[k] else ""; d["first"]=min(kwyr[k]) if kwyr[k] else None; d["last"]=max(kwyr[k]) if kwyr[k] else None
dump("keywords_dict.json",dic)
# org x keyword
orgs=[c for c in allc.coll.value_counts().index if c not in PERSON][:16]
orgk={c:C(k for ks in gen[gen.coll==c].kws for k in ks) for c in orgs}
cand=C()
for c,kc in orgk.items():
    for k,v in kc.items():
        if okk(k) and len(k)<=8: cand[k]+=v
spread={k:sum(1 for c in orgs if orgk[c][k]>=5) for k in cand}
share=[k for k,_ in cand.most_common(300) if spread[k]>=3][:40]
dump("org_keywords.json",{"orgs":orgs,"keywords":share,"matrix":[[round(orgk[c][k]/max(1,(gen.coll==c).sum()),4) for k in share] for c in orgs]})
# ---- collections
cols=[]
ct=allc.coll.value_counts()
for c in ct.index:
    g=allc[allc.coll==c]; gp=g[g.public]; cid=int(g.coll_id.iloc[0]); craw=colls_raw.get(cid,{})
    kc=C(k for ks in gp.kws for k in ks); n=len(gp)
    distinct=[k for k in sorted([k for k,v in kc.items() if v>=max(5,n*0.004) and k not in STOPK and norm(k)!=norm(c)],key=lambda k:-(kc[k]/n)/(allk[k]/N))[:25]]
    crc=gp[gp.creator.ne("")&gp.creator.ne("미상")]
    extc=crc[[norm(a.split(';')[0])!=norm(c) for a in crc.creator]]
    govc=extc[extc.creator.str.split(';').str[0].str.strip().str.contains(govpat)&~extc.creator.str.contains('연합|연대|모임|센터|협의회|네트워크|시민|환경운동')]
    yrs=gp.year.dropna()
    # sample records with file/preview
    smp=gp[(gp.files>0)|gp.preview].sort_values("year")
    smp=smp.iloc[np.linspace(0,len(smp)-1,min(8,len(smp))).astype(int)] if len(smp) else smp
    samples=[{"id":int(r.id),"title":raw[r.id]["el"].get(D+"Title",[""])[0][:60],"year":(int(r.year) if r.year==r.year else None),"type":r.rform or r.rtype,"preview":(raw[r.id]["el"].get(P+"Preview",[""])[0] if r.preview else "")} for r in smp.itertuples()]
    cols.append({"name":c,"id":cid,"slug":f"c{cid}","kind":"개인" if c in PERSON else "단체","desc":re.sub(r'<[^>]+>','',ctext(craw,"Collection Description") or ctext(craw,"Description"))[:600],
     "total":int(len(g)),"public":int(len(gp)),"private_rate":round(1-len(gp)/len(g),4),
     "access_rate":round(float(((gp.files>0)|gp.preview).mean()),4) if n else None,
     "year_min":int(yrs.min()) if len(yrs) else None,"year_max":int(yrs.max()) if len(yrs) else None,"year_median":int(yrs.median()) if len(yrs) else None,
     "share_2020s":round(float((gp.year>=2020).mean()),4),"share_pre1990":round(float((gp.year<1990).mean()),4),
     "subject_rate":round(float((gp.subject!="").mean()),4),"region_rate":round(float((gp.regions.map(len)>0).mean()),4),
     "descriptors":int(gp.descriptor.replace("",np.nan).nunique()),"added":[{"k":k,"v":int(v)} for k,v in g.added.str[:4].value_counts().sort_index().items()],
     "rtype":cnt(gp.rtype),"rform":cnt(gp.rform,12),"orig":cnt(gp.orig,3),"subject":cnt(gp.subject),
     "year":[{"k":int(y),"v":int(v)} for y,v in gp.year.value_counts().sort_index().items() if y>=1960],
     "decade":[{"k":f"{int(d)}s","v":int(v)} for d,v in gp.decade.value_counts().sort_index().items() if d>=1970],
     "regions":[{"k":k,"v":int(v)} for k,v in C(x for s in gp.regions for x in s).most_common()],
     "top_kw":[{"k":k,"v":int(v)} for k,v in kc.most_common(40) if k not in STOPK and norm(k)!=norm(c)][:25],
     "distinct_kw":[{"k":k,"v":int(kc[k])} for k in distinct],
     "kw_by_decade":{f"{int(d)}s":[{"k":k,"v":int(v)} for k,v in C(k for ks in gg.kws for k in ks if k not in STOPK and norm(k)!=norm(c)).most_common(8)] for d,gg in gp.groupby("decade") if d>=1970},
     "creators":[{"k":k,"v":int(v)} for k,v in extc.creator.value_counts().head(15).items()],"external_rate":round(len(extc)/len(crc),4) if len(crc) else None,"gov_n":int(len(govc)),"creator_n":int(len(crc)),
     "quality":{"설명":round(float((gp.desc>0).mean()),4),"키워드":round(float((gp.nkw>0).mean()),4),"생산연도":round(float(gp.year.notna().mean()),4),"주제":round(float((gp.subject!="").mean()),4),"연관":round(float(gp.rel.mean()),4),"권리":round(float((gp.rights!="").mean()),4),"원문":round(float(((gp.files>0)|gp.preview).mean()),4)} if n else {},
     "samples":samples,"url":f"https://ecoarchive.org/collections/show/id/{cid}"})
# similarity by keyword cosine
vecs={c["name"]:C(k for ks in allc[(allc.coll==c["name"])&allc.public].kws for k in ks if k not in STOPK) for c in cols}
def cos(a,b):
    na=math.sqrt(sum(v*v for v in a.values())); nb=math.sqrt(sum(v*v for v in b.values()))
    return sum(a[k]*b[k] for k in a if k in b)/(na*nb) if na and nb else 0
for c in cols:
    sims=sorted([(o["name"],cos(vecs[c["name"]],vecs[o["name"]])) for o in cols if o["name"]!=c["name"]],key=lambda x:-x[1])[:5]
    c["similar"]=[{"k":k,"v":round(v,3)} for k,v in sims if v>0]
dump("collections.json",cols)
# ---- network creator->collection
edges=[]
for c in cols:
    for e in c["creators"][:12]: edges.append({"s":e["k"],"t":c["name"],"w":e["v"]})
dump("network.json",{"edges":edges,"gov_by_year":[{"k":int(y),"v":int(v)} for y,v in gov.year.value_counts().sort_index().items() if y>=1980],
 "gov_top":[{"k":k,"v":int(v)} for k,v in gov.creator.value_counts().head(25).items()],"gov_by_coll":[{"k":k,"v":int(v)} for k,v in gov.coll.value_counts().items()],
 "gov_by_subject":[{"k":k,"v":int(v)} for k,v in gov.subject.value_counts().items() if k],
 "policy_by_year":[{"k":int(y),"v":int(v)} for y,v in gen[gen.rform.isin(["요청서/질의문","촉구서","성명서","기자회견문","의견서"])].year.value_counts().sort_index().items() if y>=1980]})
# ---- events & orgs & chronology
ev=[]
for r in df[df.type=="정보사전-사건"].itertuples():
    e=raw[r.id]["el"]; ident=e.get(D+"Identifier",[""])[0]
    rel=sum(1 for rr in raw.values() if ident and any(ident in x for x in rr["el"].get(P+"Related Case",[])))
    ev.append({"id":int(r.id),"title":e.get(D+"Title",[""])[0],"ident":ident,"start":e.get(P+"Case Start Date",[""])[0][:4],"end":e.get(P+"Case End Date",[""])[0][:4],"cls":e.get(P+"Classification of Case",[""])[0],"related":rel,"url":f"https://ecoarchive.org/items/show/{r.id}"})
dump("events.json",sorted(ev,key=lambda x:x["start"]))
og=[]
for r in df[df.type=="정보사전-조직"].itertuples():
    e=raw[r.id]["el"]
    f=re.match(r'(\d{4})',e.get(P+"Founding Date",[""])[0] or ""); d=re.match(r'(\d{4})',e.get(P+"Dissolution Date",[""])[0] or "")
    og.append({"id":int(r.id),"name":e.get(D+"Title",[""])[0],"founded":int(f.group(1)) if f else None,"dissolved":int(d.group(1)) if d else None,"cls":e.get(P+"Classification of Organization",[""])[0],"area":e.get(P+"Activity Area",[""])[0]})
dump("orgs.json",og)
ch=df[df.type=="정보사전-연표"]
dump("chronology.json",{"by_year":[{"k":int(y),"v":int(v)} for y,v in ch.year.value_counts().sort_index().items() if y>=1970],
 "by_cls":[{"k":k,"v":int(v)} for k,v in C(raw[i]["el"].get(P+"Classification of Chronology",[""])[0] for i in ch.id).most_common() if k],
 "by_org":[{"k":k,"v":int(v)} for k,v in C(raw[i]["el"].get(P+"Chronological Organization",[""])[0] for i in ch.id).most_common(15) if k]})
# ---- photos
pa=photo.copy(); pa["artist"]=[raw[i]["el"].get(P+"Originator",[""])[0] for i in pa.id]
dump("photos.json",{"n":int(len(pa)),"lic":cnt(pa.lic),"year":[{"k":int(y),"v":int(v)} for y,v in pa.year.value_counts().sort_index().items() if y>=1960],
 "regions":[{"k":k,"v":int(v)} for k,v in C(x for s in pa.regions for x in s).most_common()],
 "artists":[{"k":a,"v":int(v),"ymin":int(pa[pa.artist==a].year.min()) if pa[pa.artist==a].year.notna().any() else None,"ymax":int(pa[pa.artist==a].year.max()) if pa[pa.artist==a].year.notna().any() else None} for a,v in pa.artist.value_counts().head(60).items() if a],
 "kw":[{"k":k,"v":int(v)} for k,v in C(k for ks in pa.kws for k in ks if okk(k)).most_common(40)],
 "month":[{"k":int(m),"v":int(v)} for m,v in C(int(raw[i]["el"].get(D+"Date",["0000-00"])[0][5:7] or 0) for i in pa.id).items() if m],
 "type1":[{"k":k or "미기재","v":int(v)} for k,v in C(raw[i]["el"].get(P+"Type 1. Photography",[""])[0] for i in pa.id).most_common()],
 "exhib":[{"k":"전시이력 기재","v":int(sum(1 for i in pa.id if raw[i]["el"].get(P+"Exhibition History",[""])[0].strip()))},{"k":"미기재","v":int(sum(1 for i in pa.id if not raw[i]["el"].get(P+"Exhibition History",[""])[0].strip()))}],
 "artist_year":[{"k":a,"years":[{"k":int(y),"v":int(v)} for y,v in pa[pa.artist==a].year.value_counts().sort_index().items() if y==y]} for a,_ in pa.artist.value_counts().head(20).items() if a]})
# seasonality for records (month of Date of Creation)
mm=C()
for i in gen.id:
    d=raw[i]["el"].get(P+"Date of Creation",[""])[0]
    m=re.match(r'\d{4}-(\d{2})-\d{2}',d)
    if m: mm[int(m.group(1))]+=1
dump("season.json",[{"k":m,"v":int(mm[m])} for m in range(1,13)])
print("done", {k:len(v) for k,v in [("cols",cols),("edges",edges),("events",ev),("orgs",og),("dict",dic)]})
