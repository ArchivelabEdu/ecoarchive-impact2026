# -*- coding: utf-8 -*-
import json,re,collections,random
import pandas as pd, numpy as np
C=collections.Counter; P="Item Type Metadata:"; D="Dublin Core:"
import os; OUT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"data","timeline.json")
df=pd.read_pickle("out/df.pkl")
raw={}
for l in open("full/items.jsonl",encoding="utf-8"):
    r=json.loads(l); raw[r["id"]]=r
def title(i): return raw[i]["el"].get(D+"Title",[""])[0]
def norm(s): return re.sub(r'[\[\]\s()（）]','',s)
STOP=set(["사회","환경","기록","일반","환경운동","환경단체","정치","경제","문화","과학","사진","국제","노동","교육","생활","스포츠","종교","연예","지역","칼럼","기사","기타","환경일반","소식지","월간지","자료집","보고서","토론회","뉴스레터"])|set(norm(c) for c in df.coll.unique() if c)|set(df.coll.unique())
g=df[(df.type=="기록-일반")&df.public].copy(); g["title"]=g.id.map(title)
gk=g[g.coll!="한겨레"]
yr=g.year.dropna().astype(int)
# ---------- per-year strip
years=list(range(1980,2026))
rec_by_year={int(y):int(v) for y,v in yr.value_counts().items()}
kw_year={y:C() for y in years}
for ks,y in zip(gk.kws,gk.year):
    if y==y and 1980<=int(y)<=2025:
        for k in set(ks):
            if k not in STOP and not re.search(r'\d',k) and len(k)<=10: kw_year[int(y)][k]+=1
allk=C(k for ks in gk.kws for k in ks); N=len(gk)
def distinct(cnt,n,minc,top=8):
    sc={k:(v/n)/(allk[k]/N) for k,v in cnt.items() if v>=minc and k not in STOP}
    return [k for k,_ in sorted(sc.items(),key=lambda x:-x[1])[:top]]
year_top={y:[k for k,_ in kw_year[y].most_common(5)] for y in years}
year_distinct={y:distinct(kw_year[y],max(1,rec_by_year.get(y,1)),5,5) for y in years}
# ---------- events with search terms (initial draft; refine later)
EV_TERMS={
"낙동강 페놀 유출 사건":["페놀"],"온산병 사태":["온산"],"안면도 핵폐기장 반대":["안면도"],"환경과 개발에 관한 유엔회의":["리우","유엔환경개발회의","UNCED"],
"92년 수도권 쓰레기 대란":["쓰레기 대란","쓰레기대란","김포매립지","난지도"],"굴업도핵폐기장반대":["굴업도"],"그린벨트해제반대":["그린벨트"],"94년 낙동강 수질 오염사건":["낙동강 수질","낙동강오염","벤젠","톨루엔","낙동강 오염"],
"시화호 수질오염 대응":["시화호"],"대만 핵폐기물 수출반대":["대만"],"가야산 골프장 백지화":["가야산"],"동강댐백지화":["동강댐","동강 댐","영월댐","영월 댐","동강"],"새만금 간척사업 백지화":["새만금"],
"총선 낙천낙선운동":["낙천","낙선"],"한탄강댐백지화":["한탄강"],"매향리미군사격장폐쇄":["매향리"],"천성산 터널공사 반대":["천성산"],"부안 핵폐기장 반대":["부안","위도"],
"북한산국립공원관통도로 반대":["북한산 관통","관통도로","사패산"],"설악산케이블카 반대":["설악산","오색"],"환경비상시국회의 및 초록행동단":["환경비상시국","초록행동단"],"경인운하백지화":["경인운하","경인 운하","아라뱃길"],
"4대강반대":["4대강","사대강"],"삼성중공업 허베이스피리트호 기름유출사고":["태안","허베이","기름유출"],"밀양송전탑반대":["밀양"],"미국산 광우병 쇠고기 수입 반대":["광우병"],
"제주해군기지 건설 저지":["강정","해군기지"],"가습기살균제 참사":["가습기"],"일회용생리대 안전성 활동":["생리대"],"기후위기 대응":["기후위기","기후비상","기후행동"],
"구제역 및 AI(조류인플루엔자) 발생":["구제역","조류인플루엔자","조류독감","AI 발생","살처분"],"지구의 날":["지구의 날","지구의날"],"유전자조작 식품 수입 반대":["유전자조작","GMO","유전자변형"],"경주방폐장 건설반대":["경주방폐장","경주 방폐장","경주방사성","경주 방사성","경주 중저준위","경주중저준위"],
"도시공원일몰제":["일몰제","도시공원"],"후쿠시마 핵발전소 폭발 사고":["후쿠시마"],"제2공항 건설반대":["제2공항","제 2공항"],"신고리 5,6호기 건설 반대":["신고리"],"고리1호기 폐쇄":["고리1호기","고리 1호기","고리원전","고리 원전","고리핵발전소","고리 핵발전소"],
"블루 스카이 운동":["블루스카이","블루 스카이","Blue Sky","BLUE SKY"],"영덕 핵발전소 반대 주민투표":["영덕"],"강원도골프장반대":["강원도 골프장","강원 골프장","강원도골프장","골프장 반대","골프장반대"],"GS 칼택스 씨프린스호 해양유류오염사고":["씨프린스","여천","유류오염"],
"가리왕산 보호":["가리왕산"],"일회용플라스틱":["일회용","플라스틱"],"미세플라스틱 유해성":["미세플라스틱"],"미세먼지 저감 활동":["미세먼지"]}
SUBJ_CODE={"S0001":"반공해","S0002":"일반(정치·제도)","S0003":"반핵탈핵","S0004":"생태계보전","S0005":"대기오염","S0006":"기후에너지","S0008":"생활안전","S0009":"자원순환","S0010":"생활안전"}
events=[]
for i in df[df.type=="정보사전-사건"].id:
    e=raw[i]["el"]; t=e.get(D+"Title",[""])[0]; terms=EV_TERMS.get(t,[t])
    def hit(row_kws,row_title): return any(any(term in k for term in terms) for k in row_kws) or any(term in row_title for term in terms)
    m=[hit(ks,tt) for ks,tt in zip(g.kws,g.title)]
    sub=g[m]; ys=sub.year.dropna().astype(int)
    smp=sub[(sub.files>0)|sub.preview]
    if len(smp): smp=smp.sort_values("year").iloc[np.linspace(0,len(smp)-1,min(4,len(smp))).astype(int)]
    st=e.get(P+"Case Start Date",[""])[0][:4]; en=e.get(P+"Case End Date",[""])[0][:4]
    events.append({"id":int(i),"title":t,"start":st,"end":en,"cls":e.get(P+"Classification of Case",[""])[0],"subject":SUBJ_CODE.get(e.get(P+"Related Subject",[""])[0].split(";")[0],""),
      "terms":terms,"n":int(len(sub)),"y10":int(ys.quantile(.1)) if len(ys) else None,"y50":int(ys.median()) if len(ys) else None,"y90":int(ys.quantile(.9)) if len(ys) else None,
      "colls":[{"k":k,"v":int(v)} for k,v in sub.coll.value_counts().head(3).items() if k],
      "by_year":{int(y):int(v) for y,v in ys.value_counts().sort_index().items()},
      "samples":[{"id":int(r.id),"title":r.title[:50],"year":int(r.year) if r.year==r.year else None,"form":r.rform} for r in smp.itertuples()],
      "url":f"https://ecoarchive.org/items/show/{i}","desc":e.get(P+"Progress and Main Contents of the Case",[""])[0][:220]})
# ---------- orgs
orgs=[]; cr=g.creator.str.replace(r'[\[\]\s]','',regex=True); coll_n=g.coll.value_counts()
idmap={}
for i in df[df.type=="정보사전-조직"].id:
    e=raw[i]["el"]; ident=e.get(D+"Identifier",[""])[0]; idmap[ident]=e.get(D+"Title",[""])[0]
for i in df[df.type=="정보사전-조직"].id:
    e=raw[i]["el"]; name=e.get(D+"Title",[""])[0]
    f=re.match(r'(\d{4})',e.get(P+"Founding Date",[""])[0] or ""); d=re.match(r'(\d{4})',e.get(P+"Dissolution Date",[""])[0] or "")
    nn=norm(name); n_rec=int(cr.str.contains(re.escape(nn)).sum()) if len(nn)>=3 else 0
    n_rec=max(n_rec,int(coll_n.get(name,0)))
    orgs.append({"id":int(i),"name":name,"founded":int(f.group(1)) if f else None,"dissolved":int(d.group(1)) if d else None,"cls":e.get(P+"Classification of Organization",[""])[0],
      "areas":[SUBJ_CODE.get(x,x) for x in e.get(P+"Activity Area",[""])[0].split(";") if x],"coalition":[idmap.get(x,x) for x in e.get(P+"Coalition Organization",[""])[0].split(";") if x],
      "n_rec":n_rec,"url":f"https://ecoarchive.org/items/show/{i}","desc":e.get(P+"Main Content",[""])[0][:160]})
# ---------- chronology per year
chron=collections.defaultdict(list)
for i in df[df.type=="정보사전-연표"].id:
    e=raw[i]["el"]; y=re.match(r'(\d{4})',e.get(P+"Chronological Year",[""])[0] or e.get(P+"Chronological Start Date",[""])[0] or "")
    if y: chron[int(y.group(1))].append({"t":e.get(D+"Title",[""])[0][:70],"o":e.get(P+"Chronological Organization",[""])[0],"c":e.get(P+"Classification of Chronology",[""])[0],"d":e.get(P+"Chronological Start Date",[""])[0][:10],"id":int(i)})
for y in chron: chron[y].sort(key=lambda x:x["d"])
# ---------- eras
ERAS=[("1982–1990","반공해의 시대",1982,1990),("1991–1999","전국 조직과 반핵·수질의 시대",1991,1999),("2000–2009","새만금·국립공원·숲의 시대",2000,2009),("2010–2019","4대강·후쿠시마·탈핵·기후의 시대",2010,2019),("2020–2025","기후위기와 자원순환의 시대",2020,2025)]
eras=[]
for label,name,a,b in ERAS:
    sub=g[(g.year>=a)&(g.year<=b)]; subk=gk[(gk.year>=a)&(gk.year<=b)]
    kc=C(k for ks in subk.kws for k in ks if k not in STOP and not re.search(r'\d',k) and len(k)<=10)
    sj=sub.subject[sub.subject!=""].value_counts(); sj=sj[~sj.index.isin(["자연순환","도시생활","누추"])]
    evs=[x["title"] for x in events if x["start"].isdigit() and a<=int(x["start"])<=b]
    ogs=sorted([o for o in orgs if o["founded"] and a<=o["founded"]<=b],key=lambda o:-o["n_rec"])
    top_d=distinct(kc,len(subk),20,10)
    smp=sub[((sub.files>0)|sub.preview)&sub.kws.map(lambda ks:any(k in top_d[:6] for k in ks))]
    if len(smp): smp=smp.sort_values("year").iloc[np.linspace(0,len(smp)-1,min(5,len(smp))).astype(int)]
    eras.append({"label":label,"name":name,"a":a,"b":b,"n":int(len(sub)),"share":round(len(sub)/len(yr),3),
      "subjects":[{"k":k,"v":round(v/sj.sum(),3)} for k,v in sj.head(5).items()],"top_kw":[k for k,_ in kc.most_common(10)],"distinct_kw":top_d,
      "events":evs,"orgs_n":len(ogs),"orgs":[o["name"] for o in ogs[:8]],"colls":[{"k":k,"v":int(v)} for k,v in sub.coll.value_counts().head(4).items() if k],
      "samples":[{"id":int(r.id),"title":r.title[:50],"year":int(r.year),"form":r.rform,"coll":r.coll} for r in smp.itertuples()]})
out={"years":years,"rec_by_year":rec_by_year,"year_top":year_top,"year_distinct":year_distinct,
 "org_founded_by_year":{int(y):int(v) for y,v in C(o["founded"] for o in orgs if o["founded"]).items()},
 "chron_by_year":{int(y):len(v) for y,v in chron.items()},"chron":{int(y):v for y,v in chron.items() if y>=1980},
 "events":sorted(events,key=lambda x:x["start"] or "9999"),"orgs":orgs,"eras":eras,"subj_code":SUBJ_CODE}
json.dump(out,open(OUT,"w",encoding="utf-8"),ensure_ascii=False)
print("events n:",[(e["title"][:10],e["n"]) for e in sorted(events,key=lambda x:-x["n"])[:12]])
print("orgs with records:",sum(1 for o in orgs if o["n_rec"]>0),"| founded known:",sum(1 for o in orgs if o["founded"]),"| coalition edges:",sum(len(o["coalition"]) for o in orgs))
print("eras:",[(e["label"],e["n"],e["orgs_n"],len(e["events"]),len(e["samples"])) for e in eras])
import os; print("size",os.path.getsize(OUT)//1024,"KB")
