# -*- coding: utf-8 -*-
"""Static site builder: templates/*.html + data/*.json -> docs/"""
import json, os, shutil, sys
from jinja2 import Environment, FileSystemLoader
import markdown
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D=lambda n: json.load(open(os.path.join(ROOT,"data","holdings",n),encoding="utf-8"))
S=D("summary.json"); H=D("holdings.json"); COLS=D("collections.json"); KW=D("keywords_windows.json"); SER=D("keywords_series.json")
CH=D("keywords_change.json"); LIFE=D("keywords_life.json"); G=D("keywords_cooc.json"); OK=D("org_keywords.json"); NW=D("network.json")
EV=D("events.json"); OG=D("orgs.json"); CHR=D("chronology.json"); PH=D("photos.json"); SEASON=D("season.json"); DICT_N=len(D("keywords_dict.json"))
SLUG={c["name"]:c["slug"] for c in COLS}
INTRO=json.load(open(os.path.join(ROOT,"content","collections_intro.json"),encoding="utf-8"))
for c in COLS:
    i=INTRO.get(c["name"]); c["who"]=i["who"] if i else c["desc"]; c["what"]=i["what"] if i else ""
env=Environment(loader=FileSystemLoader(os.path.join(ROOT,"templates")),autoescape=False)
env.filters["tojson"]=lambda v: json.dumps(v,ensure_ascii=False).replace("</","<\\/")
OUT=os.path.join(ROOT,"docs")
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
shutil.copytree(os.path.join(ROOT,"assets"),os.path.join(OUT,"assets"))
shutil.copytree(os.path.join(ROOT,"data","holdings"),os.path.join(OUT,"data"))
shutil.copytree(os.path.join(ROOT,"report"),os.path.join(OUT,"report"))
shutil.copytree(os.path.join(ROOT,"games"),os.path.join(OUT,"games"))
open(os.path.join(OUT,".nojekyll"),"w").close()
SECTIONS={
 "holdings":("소장 현황",[("규모와 구성","holdings/composition.html"),("시간","holdings/time.html"),("주제","holdings/subject.html"),("지역","holdings/region.html"),("메타데이터 품질","holdings/quality.html")]),
 "keywords":("키워드",[("연대별 변화","keywords/change.html"),("키워드 생애곡선","keywords/life.html"),("공출현 네트워크","keywords/cooc.html"),("단체별 키워드","keywords/orgs.html"),("키워드 사전","keywords/dict.html")]),
 "more":("더보기",[("네트워크","network/index.html"),("사진 아카이브","photos/index.html"),("보드게임","games/index.html"),("보드게임 만들기 가이드","guide/index.html"),("임팩트 측정","impact/index.html"),("데이터·방법","data/index.html"),("소개","about.html")]),
 "collections":("컬렉션",[("컬렉션 비교","collections/index.html")]+[(c["name"],f"collections/{c['slug']}.html") for c in COLS]),
}
def render(tpl,path,**ctx):
    depth=path.count("/"); root="../"*depth
    sec=ctx.get("section"); sub=SECTIONS.get(sec)
    nav=None
    if sub:
        items=sub[1]; idx=next((i for i,(n,p_) in enumerate(items) if p_==path),None)
        nav={"title":sub[0],"items":items,"idx":idx,"prev":items[idx-1] if idx not in (None,0) else None,"next":items[idx+1] if idx is not None and idx+1<len(items) else None,"path":path}
    html=env.get_template(tpl).render(S=S,root=root,SLUG=SLUG,NAV=nav,**ctx)
    p=os.path.join(OUT,path); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,"w",encoding="utf-8").write(html)
md=lambda f: markdown.markdown(open(os.path.join(ROOT,"content",f),encoding="utf-8").read(),extensions=["tables"])
# ---- indicators for impact page
fmtn=lambda n: f"{n:,}"; pct=lambda x: f"{x*100:.1f}%"
gen=S["gen_public"]
IND=[
 ("A. 학술·지식 생산",[
  ("A1 원문 제공률","파일 또는 임베드가 있는 공개 기록 비율",pct(S["access_rate"]),"files, Preview"),
  ("A2 디지털 원문 분량","쪽수 합계(기재분)",fmtn(S["pages_sum"])+"쪽","Size/Quantity"),
  ("A3 메타데이터 완성도","제목·설명·키워드·생산자·생산연도·주제·원문 7항목 평균",pct(sum([1,H["quality"]["설명"],S["kw_rate"],1,S["year_rate"],S["subject_rate"],S["access_rate"]])/7),"각 필드"),
  ("A4 맥락 연결 밀도","연관 기록·사건·연표·조직 중 1개 이상",pct(S["rel_rate"]),"Related *"),
  ("A5 키워드 밀도 / 어휘 규모","건당 키워드 수 / 고유 키워드 수",f"{S['kw_mean']}개 / {fmtn(S['keywords_unique'])}개","Keyword, tags"),
  ("A6 큐레이션 재소환률","전시·칼럼이 인용한 고유 기록 / 공개 기록","348건 (0.36%)","exhibits"),
  ("A7 시기 커버리지","1990~2000년대 / 1980년대 이전 비중","64.2% / 2.4%","Year of Creation")]),
 ("B. 사회·운동사",[
  ("B1 운동 네트워크 폭","고유 생산자 수 / 기증주체 외부 생산 비율",f"{fmtn(S['creators_unique'])} / {pct(S['external_rate'])}","Creator vs collection"),
  ("B2 컬렉션 간 교류","생산자→기증주체 그래프","네트워크 페이지","Creator, collection"),
  ("B3 의제 발신 기록 비중","보도자료·성명서·촉구서·공문 등",f"{fmtn(S['adv_n'])}건 ({pct(S['adv_n']/gen)})","Format of Records"),
  ("B4 사건별 증거 밀도","정보사전-사건 47건 각각의 연결 기록 수","환경운동 40년 페이지","Related Case"),
  ("B5 세대 기록 균형","≤1980s / 1990~2000s / 2010s+","2.4 / 64.2 / 33.4%","Year of Creation"),
  ("B6 현장 커버리지","키워드·태그로 식별된 시도 분포",f"기록 {pct(H['region_rate'])} 식별, 사진 98.6%","Keyword, Filming Location")]),
 ("C. 정책·제도",[
  ("C1 공공기관 생산 문서","생산자가 행정·공공기관인 기록",f"{fmtn(S['gov_n'])}건 ({pct(S['gov_n']/S['creator_n'])})","Creator"),
  ("C2 정책 대응 기록","요청서·촉구서·성명서·기자회견문·의견서",f"{fmtn(S['policy_n'])}건","Format of Records"),
  ("C3 정책 연표 항목","연표구분 '정부'·'법원'",f"{sum(d['v'] for d in CHR['by_cls'] if d['k'] in ('정부','법원'))}건","Classification of Chronology")]),
 ("D. 이용자 경험",[
  ("D1 매체 다양성","기록유형 분포","문서 51% · 간행물 34% · 사진 9% · 영상 3%","Type of Records"),
  ("D2 언어 접근성","한국어 외 언어 비중","4.2%","Language of Records"),
  ("D3 재이용 준비도","라이선스 명시율","사진 93.1% / 기록-일반 "+pct(S["rights_rate"]),"Copyright, Rights"),
  ("D4 이용자 기여","오류신고·목록받기 건수","미측정 (GA4 이벤트 필요)","Corrections, ?output=csv")]),
 ("E. 조직·운영",[
  ("E1 기록 기술 인력","기술자 수 / 상위 10명 집중도","29명 / 64%","Descriptor"),
  ("E2 기술·등록 활동 추이","연도별 등록 건수","2020 39.5천 → 2025 58 → 2026 17.9천(일괄)","added, Description Date"),
  ("E3 컬렉션 활성도","2020년대 생산 기록 비중","숲과나눔 84% ~ 한겨레 0%","Year × collection"),
  ("E4 비공개율","비공개 / 등록",pct(1-S["public"]/S["items"])+" (정태석 86.5% ~ 0%)","public"),
  ("E5 원본 형태","비전자 : 전자","75.3 : 24.7","Format of Originals")]),
]
FILES=[("REPORT","환경아카이브 풀숲·환경사진아카이브·공간풀숲 임팩트 측정 보고서 v1.0 (PDF, 82쪽, 5.2MB, 2026-10-01 발행)"),("summary.json","핵심 수치"),("holdings.json","유형·형태·연도·주제·지역·품질·등록 추이"),("collections.json","컬렉션 34개 상세(유형·연도·주제·지역·키워드·생산자·품질·예시)"),("keywords_windows.json","5년 단위 상위·특징 키워드"),("keywords_series.json","상위 400 키워드의 연도별 건수"),("keywords_life.json","키워드 등장·정점·퇴장"),("keywords_change.json","연대 간 급상승·급락"),("keywords_cooc.json","공출현 네트워크"),("keywords_dict.json","키워드 사전(3건 이상)"),("org_keywords.json","단체 × 공통 키워드"),("network.json","생산자→기증주체, 공공기관 문서"),("events.json","사건 47건"),("orgs.json","조직 전거 542건"),("chronology.json","연표 집계"),("photos.json","작품사진 집계"),("season.json","생산 월 분포")]
render("index.html","index.html",title="홈",H=H,COLS=COLS,KW=KW,section="home")
render("holdings_composition.html","holdings/composition.html",title="규모와 구성",H=H,section="holdings")
render("holdings_time.html","holdings/time.html",title="시간",H=H,SEASON=SEASON,YBC=H["year_by_coll"],section="holdings")
render("holdings_subject.html","holdings/subject.html",title="주제",H=H,section="holdings")
render("holdings_region.html","holdings/region.html",title="지역",H=H,COLS=COLS,section="holdings")
render("holdings_quality.html","holdings/quality.html",title="메타데이터 품질",H=H,COLS=COLS,section="holdings")
render("collections_index.html","collections/index.html",title="컬렉션 비교",COLS=COLS,section="collections")
for c in COLS: render("collection.html",f"collections/{c['slug']}.html",title=c["name"],C=c,section="collections",desc=f"{c['name']} 컬렉션 {c['total']:,}건의 구성·시기·주제·지역·키워드")
render("keywords_change.html","keywords/change.html",title="연대별 키워드 변화",KW=KW,SER=SER,CH=CH,LIFE=LIFE,section="keywords")
render("keywords_life.html","keywords/life.html",title="키워드 생애곡선",SER=SER,section="keywords")
render("keywords_cooc.html","keywords/cooc.html",title="공출현 네트워크",G=G,section="keywords")
render("keywords_orgs.html","keywords/orgs.html",title="단체별 키워드",OK=OK,COLS=COLS,section="keywords")
render("keywords_dict.html","keywords/dict.html",title="키워드 사전",N=DICT_N,section="keywords")
T=D("timeline.json"); ERA_TEXT=json.load(open(os.path.join(ROOT,"content","eras.json"),encoding="utf-8"))
SUBJ_COLOR={"생태계보전":"#2f6f4e","반핵탈핵":"#8ab17d","기후에너지":"#e9c46a","반공해":"#e76f51","자원순환":"#6d597a","생활안전":"#b56576","국제연대":"#355070","대기오염":"#a8dadc","재난재해":"#457b9d","도시환경":"#1d3557","일반":"#f4a261"}
render("timeline.html","timeline/index.html",title="환경운동 40년",T=T,KW=KW,YBC=H["year_by_coll"],ERA_TEXT=ERA_TEXT,SUBJ_COLOR=SUBJ_COLOR,section="timeline",desc="풀숲 기록의 연도·주제·키워드와 사건 47건·조직 542건·연표 3,617건으로 본 한국 환경운동 40년")
render("network.html","network/index.html",title="네트워크",NW=NW,COLS=COLS,section="more")
render("photos.html","photos/index.html",title="사진 아카이브",PH=PH,section="more")
render("impact.html","impact/index.html",title="임팩트 측정",IND=IND,section="more")
render("data.html","data/index.html",title="데이터·방법",FILES=FILES,METHODS=md("methods.md"),section="more")
render("about.html","about.html",title="소개",ABOUT=md("about.md"),section="more")
render("guide.html","guide/index.html",title="보드게임 만들기 가이드",GUIDE=md("guide.md"),section="more",desc="환경아카이브 풀숲 데이터로 보드게임을 만드는 방법: 카드 덱 JSON, 집계 데이터, Omeka API, 템플릿, 이용 조건")
print("built", sum(len(f) for _,_,f in os.walk(OUT)), "files ->", OUT)
