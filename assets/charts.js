/* charts.js — ECharts helpers for ecoarchive-impact2026 */
const PAL = ["#2f6f4e","#8ab17d","#e9c46a","#f4a261","#e76f51","#6d597a","#b56576","#355070","#a8dadc","#457b9d","#1d3557","#999999","#c9ada7","#9a8c98"];
const SUBJ = {"생태계보전":"#2f6f4e","반핵탈핵":"#8ab17d","기후에너지":"#e9c46a","반공해":"#e76f51","자원순환":"#6d597a","생활안전":"#b56576","국제연대":"#355070","대기오염":"#a8dadc","재난재해":"#457b9d","도시환경":"#1d3557","일반":"#f4a261","기타":"#999999"};
const FONT = "Pretendard Variable, Pretendard, -apple-system, Apple SD Gothic Neo, Noto Sans KR, sans-serif";
const BASE = {textStyle:{fontFamily:FONT,color:"#1f2a24"},color:PAL,animationDuration:500,
  tooltip:{backgroundColor:"rgba(255,255,255,.96)",borderColor:"#e3e8e4",textStyle:{color:"#1f2a24",fontFamily:FONT}}};
const fmtN = n => (n==null?"—":Number(n).toLocaleString("ko-KR"));
const fmtP = (x,d=1) => (x==null?"—":(x*100).toFixed(d)+"%");
const charts = [];
function mk(el){ const dom = typeof el==="string"?document.getElementById(el):el; if(!dom) return null; const c = echarts.init(dom,null,{renderer:"canvas"}); charts.push(c); return c; }
window.addEventListener("resize",()=>charts.forEach(c=>c.resize()));
function opt(o){ return Object.assign({},BASE,o); }
function subjColor(k){ return SUBJ[k]||"#999"; }

/* horizontal bar: items [{k,v}] */
function hbar(el, items, o={}){
  const c=mk(el); if(!c) return; const it=[...items].reverse();
  c.setOption(opt({grid:{left:o.left||150,right:70,top:o.title?40:10,bottom:20,containLabel:false},
    title:o.title?{text:o.title,left:0,textStyle:{fontSize:14}}:null,
    xAxis:{type:"value",splitLine:{lineStyle:{color:"#eef2ef"}},axisLabel:{formatter:v=>o.pct?(v*100).toFixed(0)+"%":fmtN(v)}},
    yAxis:{type:"category",data:it.map(d=>d.k),axisLabel:{fontSize:12,width:o.left?o.left-10:140,overflow:"truncate"},axisTick:{show:false},axisLine:{show:false}},
    tooltip:{trigger:"axis",axisPointer:{type:"shadow"},valueFormatter:v=>o.pct?fmtP(v):fmtN(v)},
    series:[{type:"bar",data:it.map(d=>({value:d.v,itemStyle:{color:o.color?o.color(d):"#2f6f4e"}})),barMaxWidth:22,
      label:{show:true,position:"right",fontSize:11,color:"#5f6b65",formatter:p=>o.pct?fmtP(p.value):fmtN(p.value)}}]}));
}
/* vertical bar by category (years) */
function vbar(el, items, o={}){
  const c=mk(el); if(!c) return;
  c.setOption(opt({grid:{left:60,right:20,top:o.title?44:20,bottom:40},title:o.title?{text:o.title,left:0,textStyle:{fontSize:14}}:null,
    xAxis:{type:"category",data:items.map(d=>d.k),axisLabel:{interval:o.interval??"auto",rotate:o.rotate||0}},
    yAxis:{type:"value",splitLine:{lineStyle:{color:"#eef2ef"}},axisLabel:{formatter:v=>o.pct?(v*100).toFixed(0)+"%":fmtN(v)}},
    tooltip:{trigger:"axis",valueFormatter:v=>o.pct?fmtP(v):fmtN(v)},
    dataZoom:o.zoom?[{type:"inside"},{type:"slider",height:18,bottom:6}]:null,
    series:[{type:"bar",data:items.map(d=>d.v),itemStyle:{color:o.color||"#2f6f4e"},barMaxWidth:30,markLine:o.avg?{silent:true,symbol:"none",lineStyle:{color:"#e76f51",type:"dashed"},data:[{type:"average",name:"평균"}]}:null}]}));
}
function donut(el, items, o={}){
  const c=mk(el); if(!c) return;
  c.setOption(opt({tooltip:{trigger:"item",formatter:p=>`${p.name}<br><b>${fmtN(p.value)}</b> (${p.percent}%)`},
    legend:{bottom:0,type:"scroll",textStyle:{fontSize:11}},
    series:[{type:"pie",radius:["42%","70%"],center:["50%","45%"],data:items.map(d=>({name:d.k,value:d.v,itemStyle:o.subj?{color:subjColor(d.k)}:null})),
      label:{formatter:"{b}\n{d}%",fontSize:11},itemStyle:{borderColor:"#fff",borderWidth:2}}]}));
}
/* stacked bar: cats[], series [{name,data[]}] */
function stacked(el, cats, series, o={}){
  const c=mk(el); if(!c) return;
  const horiz=o.horizontal;
  const tot=cats.map((_,i)=>series.reduce((s,x)=>s+(x.data[i]||0),0));
  const ser=series.map((s,i)=>({name:s.name,type:"bar",stack:"a",barMaxWidth:28,itemStyle:{color:o.subj?subjColor(s.name):(s.color||PAL[i%PAL.length])},
    data:s.data.map((v,j)=>o.percent?(tot[j]?v/tot[j]:0):v)}));
  c.setOption(opt({grid:{left:horiz?(o.left||150):60,right:20,top:10,bottom:60},legend:{bottom:0,type:"scroll",textStyle:{fontSize:11}},
    tooltip:{trigger:"axis",axisPointer:{type:"shadow"},valueFormatter:v=>o.percent?fmtP(v):fmtN(v)},
    [horiz?"yAxis":"xAxis"]:{type:"category",data:horiz?[...cats].reverse():cats,axisLabel:{fontSize:11,rotate:horiz?0:(o.rotate||0)},inverse:false},
    [horiz?"xAxis":"yAxis"]:{type:"value",max:o.percent?1:null,splitLine:{lineStyle:{color:"#eef2ef"}},axisLabel:{formatter:v=>o.percent?(v*100).toFixed(0)+"%":fmtN(v)}},
    series:horiz?ser.map(s=>({...s,data:[...s.data].reverse()})):ser}));
}
/* heatmap: rows[], cols[], matrix[r][c] (0..1 or counts) */
function heat(el, rows, cols, m, o={}){
  const c=mk(el); if(!c) return;
  const data=[]; let mx=0;
  rows.forEach((r,i)=>cols.forEach((k,j)=>{const v=m[i][j]||0; data.push([j,i,v]); if(v>mx) mx=v;}));
  c.setOption(opt({grid:{left:o.left||170,right:20,top:10,bottom:o.bottom||90},
    xAxis:{type:"category",data:cols,position:"bottom",axisLabel:{rotate:o.rotate??45,fontSize:11},splitArea:{show:true}},
    yAxis:{type:"category",data:rows,inverse:true,axisLabel:{fontSize:11,width:o.left?o.left-14:156,overflow:"truncate"},splitArea:{show:true}},
    visualMap:{min:0,max:o.max||mx||1,show:false,inRange:{color:["#f7faf7","#cfe3d5","#8ab17d","#2f6f4e","#163b28"]}},
    tooltip:{formatter:p=>`${rows[p.value[1]]} × ${cols[p.value[0]]}<br><b>${o.pct?fmtP(p.value[2]):fmtN(p.value[2])}</b>`},
    series:[{type:"heatmap",data,label:{show:o.label!==false,fontSize:9.5,formatter:p=>{const v=p.value[2]; if(o.pct) return v>=(o.min||0.05)?(v*100).toFixed(0)+"%":""; return v>=(o.min||1)?fmtN(v):"";}},
      itemStyle:{borderColor:"#fff",borderWidth:1}}]}));
}
/* multi-line: x[], series [{name,data[]}] */
function lines(el, x, series, o={}){
  const c=mk(el); if(!c) return;
  c.setOption(opt({grid:{left:60,right:o.endLabel?120:20,top:20,bottom:o.legend===false?30:60},legend:o.legend===false?null:{bottom:0,type:"scroll",textStyle:{fontSize:11}},
    xAxis:{type:"category",data:x,boundaryGap:false},yAxis:{type:"value",splitLine:{lineStyle:{color:"#eef2ef"}},axisLabel:{formatter:v=>o.pct?(v*100).toFixed(1)+"%":fmtN(v)}},
    tooltip:{trigger:"axis",valueFormatter:v=>o.pct?fmtP(v,2):fmtN(v)},
    series:series.map((s,i)=>({name:s.name,type:"line",smooth:.3,showSymbol:false,lineStyle:{width:2.2},data:s.data,color:s.color||PAL[i%PAL.length],
      endLabel:o.endLabel?{show:true,formatter:"{a}",fontSize:11}:null,emphasis:{focus:"series"}}))}));
}
/* bump chart: wins[], items {name: [rank per window or null]} */
function bump(el, wins, items, o={}){
  const c=mk(el); if(!c) return; const names=Object.keys(items); const K=o.k||15;
  c.setOption(opt({grid:{left:40,right:130,top:20,bottom:30},
    xAxis:{type:"category",data:wins,boundaryGap:false,axisLine:{show:false},axisTick:{show:false},axisLabel:{fontWeight:600}},
    yAxis:{type:"value",inverse:true,min:1,max:K,interval:1,axisLabel:{formatter:v=>v+"위"},splitLine:{lineStyle:{color:"#eef2ef"}}},
    tooltip:{trigger:"item",formatter:p=>`${p.seriesName}<br>${wins[p.dataIndex]}: <b>${p.value}위</b>`},
    series:names.map((n,i)=>({name:n,type:"line",smooth:true,symbolSize:9,lineStyle:{width:3,opacity:.85},data:items[n].map(r=>(r&&r<=K)?r:null),connectNulls:false,color:PAL[i%PAL.length],
      endLabel:{show:true,formatter:"{a}",fontSize:11,distance:8},emphasis:{focus:"series",lineStyle:{width:5}},blur:{lineStyle:{opacity:.12}}}))}));
}
/* theme river: rows [[date,value,name],...] */
function river(el, rows, names, o={}){
  const c=mk(el); if(!c) return;
  c.setOption(opt({tooltip:{trigger:"axis",axisPointer:{type:"line"}},legend:{bottom:0,type:"scroll",textStyle:{fontSize:11},data:names},
    singleAxis:{type:"category",top:20,bottom:70,axisTick:{show:false},axisLine:{show:false},axisLabel:{fontWeight:600}},
    series:[{type:"themeRiver",emphasis:{itemStyle:{shadowBlur:10,shadowColor:"rgba(0,0,0,.2)"}},data:rows,label:{show:false}}]}));
}
/* force graph: nodes [{id,n,cat}], edges [{s,t,w}] */
function graph(el, nodes, edges, o={}){
  const c=mk(el); if(!c) return;
  const mx=Math.max(...nodes.map(n=>n.n||1));
  c.setOption(opt({tooltip:{formatter:p=>p.dataType==="edge"?`${p.data.source} → ${p.data.target}: <b>${fmtN(p.data.value)}</b>`:`${p.data.name}<br>${fmtN(p.data.n)}건`},
    legend:o.cats?{bottom:0,data:o.cats.map(x=>x.name)}:null,
    series:[{type:"graph",layout:"force",roam:true,draggable:true,categories:o.cats||null,
      force:{repulsion:o.rep||120,edgeLength:o.len||[40,140],gravity:.08,friction:.4},
      data:nodes.map(n=>({name:n.id,n:n.n,category:n.cat,symbolSize:8+Math.sqrt((n.n||1)/mx)*(o.maxSize||42),
        label:{show:(n.n||0)>=(o.labelMin||0),fontSize:11},itemStyle:n.color?{color:n.color}:null})),
      links:edges.map(e=>({source:e.s,target:e.t,value:e.w,lineStyle:{width:.6+Math.log2(e.w||1),opacity:.35,curveness:.1}})),
      lineStyle:{color:"source"},emphasis:{focus:"adjacency",label:{show:true}}}]}));
}
function radar(el, ind, vals, o={}){
  const c=mk(el); if(!c) return;
  c.setOption(opt({radar:{indicator:ind.map(k=>({name:k,max:1})),radius:"64%",axisName:{color:"#5f6b65",fontSize:11},splitArea:{areaStyle:{color:["#fff","#f6f9f6"]}}},
    tooltip:{},series:[{type:"radar",data:vals.map((v,i)=>({value:v.data,name:v.name,areaStyle:{opacity:.18},lineStyle:{width:2},color:PAL[i]}))},]}));
}
/* gantt-like range bars: items [{k,first,last,peak,n}] */
function ranges(el, items, o={}){
  const c=mk(el); if(!c) return; const it=[...items].reverse();
  c.setOption(opt({grid:{left:130,right:30,top:10,bottom:30},
    xAxis:{type:"value",min:o.min||1980,max:o.max||2026,splitLine:{lineStyle:{color:"#eef2ef"}},axisLabel:{formatter:v=>v}},
    yAxis:{type:"category",data:it.map(d=>d.k),axisLabel:{fontSize:11},axisTick:{show:false},axisLine:{show:false}},
    tooltip:{formatter:p=>{const d=it[p.dataIndex];return `${d.k}<br>${d.first}–${d.last} (정점 ${d.peak})<br>${fmtN(d.n)}건`}},
    series:[{type:"custom",renderItem:(params,api)=>{const y=api.coord([0,api.value(0)])[1];const x1=api.coord([api.value(1),0])[0];const x2=api.coord([api.value(2),0])[0];const xp=api.coord([api.value(3),0])[0];const h=api.size([0,1])[1]*.55;
        return {type:"group",children:[{type:"rect",shape:{x:x1,y:y-h/2,width:Math.max(2,x2-x1),height:h,r:3},style:{fill:"#8ab17d"}},{type:"circle",shape:{cx:xp,cy:y,r:h*.42},style:{fill:"#2f6f4e"}}]}},
      encode:{x:[1,2,3],y:0},data:it.map((d,i)=>[i,d.first,d.last,d.peak])}]}));
}
/* sortable table */
function sortable(tbl){
  const ths=tbl.querySelectorAll("th"); ths.forEach((th,i)=>th.addEventListener("click",()=>{
    const tb=tbl.tBodies[0]; const rows=[...tb.rows]; const num=th.classList.contains("n"); const asc=!(th.dataset.asc==="1"); ths.forEach(t=>t.dataset.asc="");
    th.dataset.asc=asc?"1":"0"; rows.sort((a,b)=>{let x=a.cells[i].dataset.v??a.cells[i].textContent,y=b.cells[i].dataset.v??b.cells[i].textContent; if(num){x=parseFloat(x)||0;y=parseFloat(y)||0;return asc?x-y:y-x;} return asc?x.localeCompare(y,"ko"):y.localeCompare(x,"ko");});
    rows.forEach(r=>tb.appendChild(r));}));
}
document.addEventListener("DOMContentLoaded",()=>{document.querySelectorAll("table.t.sortable").forEach(sortable);
  const b=document.querySelector(".burger"); if(b) b.addEventListener("click",()=>document.querySelector(".menu").classList.toggle("open"));});
