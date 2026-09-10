/* 공통: 카드 덱 로드, 셔플, 주제색 */
const SUBJ={"생태계보전":"#2f6f4e","반핵탈핵":"#8ab17d","기후에너지":"#e9c46a","반공해":"#e76f51","자원순환":"#6d597a","생활안전":"#b56576","국제연대":"#355070","대기오염":"#a8dadc","재난재해":"#457b9d","도시환경":"#1d3557","일반(정치·제도)":"#f4a261","일반":"#f4a261"};
const shuffle=a=>{a=[...a];for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;};
const pick=(a,n)=>shuffle(a).slice(0,n);
const fmt=n=>Number(n).toLocaleString("ko-KR");
async function loadCards(){const r=await fetch("../data/cards.json");return r.json();}
function esc(s){return String(s||"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}
