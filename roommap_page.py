ROOMMAP_HTML = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover">
<title>Room Map — บ้านเพื่อน</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap">
<style>
:root {
  --bg:#080c16;--surface:#101627;--surface2:#16203a;--border:#1f2e4a;
  --fg:#dde5f5;--fg2:#5f7299;--accent:#3d7ee8;--accent-glow:rgba(61,126,232,.18);
  --garden:#0a2015;--garden-fg:#2d7a4a;
  --h0-bg:#111827;--h0-fg:#3a4f6e;
  --h1-bg:#0d3320;--h1-fg:#34c066;
  --h2-bg:#185c35;--h2-fg:#72e09a;
  --h3-bg:#5a3000;--h3-fg:#f5a623;
  --h4-bg:#5a0f0f;--h4-fg:#f56565;
  --c-ov:#4080e0;--c-tp:#34c066;--c-rd:#d4a017;
  --fin-calc:#3d7ee8;--fin-ocr:#34c066;--fin-shop:#bc8cff;
  color-scheme:dark;
  font-family:'Sarabun',system-ui,sans-serif;
}
@media(prefers-color-scheme:light){:root:not([data-theme="dark"]){
  --bg:#edf1fb;--surface:#fff;--surface2:#e4eafc;--border:#c5d2ee;
  --fg:#0d1a38;--fg2:#5a6e95;--accent:#2356c7;--accent-glow:rgba(35,86,199,.12);
  --garden:#cee8d5;--garden-fg:#1a6637;
  --h0-bg:#dde5f8;--h0-fg:#8099c8;
  --h1-bg:#bbf7d0;--h1-fg:#14532d;
  --h2-bg:#4ade80;--h2-fg:#052e16;
  --h3-bg:#fde68a;--h3-fg:#78350f;
  --h4-bg:#fca5a5;--h4-fg:#7f1d1d;
  --c-ov:#1d4ed8;--c-tp:#166534;--c-rd:#92400e;
  --fin-calc:#1d4ed8;--fin-ocr:#166534;--fin-shop:#7c3aed;
  color-scheme:light;
}}
:root[data-theme="light"]{
  --bg:#edf1fb;--surface:#fff;--surface2:#e4eafc;--border:#c5d2ee;
  --fg:#0d1a38;--fg2:#5a6e95;--accent:#2356c7;--accent-glow:rgba(35,86,199,.12);
  --garden:#cee8d5;--garden-fg:#1a6637;
  --h0-bg:#dde5f8;--h0-fg:#8099c8;
  --h1-bg:#bbf7d0;--h1-fg:#14532d;
  --h2-bg:#4ade80;--h2-fg:#052e16;
  --h3-bg:#fde68a;--h3-fg:#78350f;
  --h4-bg:#fca5a5;--h4-fg:#7f1d1d;
  --c-ov:#1d4ed8;--c-tp:#166534;--c-rd:#92400e;
  --fin-calc:#1d4ed8;--fin-ocr:#166534;--fin-shop:#7c3aed;
  color-scheme:light;
}
*,*::before,*::after{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);margin:0;padding:16px;padding-block:16px;font-family:'Sarabun',system-ui,sans-serif}
h1{font-size:1.05rem;font-weight:700;margin:0 0 12px;letter-spacing:.02em}
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:14px}
.controls input[type=date]{background:var(--surface);border:1px solid var(--border);color:var(--fg);padding:6px 9px;border-radius:6px;font:500 .83rem 'Sarabun',sans-serif}
.btn{background:var(--accent);color:#fff;border:none;padding:6px 14px;border-radius:6px;font:600 .83rem 'Sarabun',sans-serif;cursor:pointer}
.badge{font-size:.68rem;background:var(--surface2);color:var(--fg2);padding:3px 8px;border-radius:20px;border:1px solid var(--border)}
.quick-btns{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.qbtn{background:var(--surface2);color:var(--fg2);border:1px solid var(--border);padding:5px 12px;border-radius:20px;font:500 .78rem 'Sarabun',sans-serif;cursor:pointer;transition:background .1s,color .1s}
.qbtn:hover,.qbtn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:14px}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:10px 12px}
.kpi .n{font:700 1.7rem/1 'JetBrains Mono',monospace;font-variant-numeric:tabular-nums}
.kpi .l{font-size:.68rem;color:var(--fg2);margin-top:3px}
#k1{color:var(--c-ov)}#k2{color:var(--c-tp)}#k3{color:var(--c-rd)}
.legend{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px;font-size:.68rem;color:var(--fg2);align-items:center}
.ls{display:flex;gap:4px;align-items:center}
.lsw{width:12px;height:12px;border-radius:2px}
.sec-label{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--fg2);margin-bottom:5px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:10px 12px;margin-bottom:10px}
.floor-tag{font-size:.62rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--fg2);margin-bottom:4px}
.room-row{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.room-row:last-child{margin-bottom:0}
.floor-sep{height:1px;background:var(--border);margin:6px 0 10px}
.b-top{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px}
.b-mid{display:flex;gap:8px;min-height:200px}
.b-col{display:flex;flex-direction:column;gap:6px;flex-shrink:0}
.garden{flex:1;background:var(--garden);border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:var(--garden-fg);font-size:.78rem;font-weight:500;line-height:1.8;border:1px solid rgba(45,122,74,.25);min-height:140px}
.room{width:54px;height:50px;border-radius:6px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;border:2px solid transparent;transition:transform .1s,box-shadow .1s;flex-shrink:0;user-select:none;position:relative}
.room .rn{font:500 .88rem/1 'JetBrains Mono',monospace}
.room .rc{font:500 .58rem/1 'JetBrains Mono',monospace;margin-top:3px;opacity:.85}
.room:hover{transform:scale(1.07)}
.room.selected{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow)}
.room.xf-from{outline:2px dashed #f5a623;outline-offset:2px}
.room.xf-to{outline:2px dashed #34c066;outline-offset:2px}
.room.has-maint::after{content:'🔧';position:absolute;top:2px;right:2px;font-size:.5rem;line-height:1}
.detail{background:var(--surface2);border:1px solid var(--accent);border-radius:10px;padding:14px;margin-bottom:10px}
.detail h3{font-size:.95rem;margin:0 0 10px}
.dg{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.ds{background:var(--surface);border-radius:6px;padding:8px 10px}
.ds .dn{font:700 1.3rem/1 'JetBrains Mono',monospace;margin-bottom:3px}
.ds .dl{font-size:.68rem;color:var(--fg2)}
.ds:nth-child(1) .dn{color:var(--c-ov)}
.ds:nth-child(2) .dn{color:var(--c-tp)}
.ds:nth-child(3) .dn{color:var(--c-rd)}
.d-xfers{margin-top:10px;font-size:.78rem;line-height:1.7}
.d-maint{margin-top:10px;padding:8px 10px;border-radius:6px;background:rgba(245,166,35,.08);border:1px solid rgba(245,166,35,.2);font-size:.78rem;line-height:1.6}
.d-maint-title{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#f5a623;margin-bottom:4px}
.xlog-title{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--fg2);margin-bottom:7px}
.xfer{display:flex;align-items:center;gap:10px;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:8px 11px;font-size:.8rem;margin-bottom:6px;flex-wrap:wrap}
.xdate{color:var(--fg2);font:500 .72rem 'JetBrains Mono',monospace;white-space:nowrap;min-width:70px}
.xarrow{display:flex;align-items:center;gap:6px;font-weight:600}
.xfrom{background:rgba(245,166,35,.15);color:#f5a623;padding:2px 7px;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:.8rem}
.xto{background:rgba(52,192,102,.15);color:#34c066;padding:2px 7px;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:.8rem}
.xnote{color:var(--fg2);font-size:.72rem;margin-left:auto}
.fin-panel{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin-bottom:10px}
.fin-title{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--fg2);margin-bottom:10px}
.fin-row{display:flex;align-items:center;gap:10px;border-bottom:1px solid var(--border);padding:8px 0}
.fin-row:last-of-type{border-bottom:none;padding-bottom:0}
.fin-icon{font-size:.9rem;flex-shrink:0}
.fin-label{flex:1;font-size:.83rem}
.fin-sub{font-size:.65rem;color:var(--fg2);margin-top:1px}
.fin-val{font:700 1rem/1 'JetBrains Mono',monospace;font-variant-numeric:tabular-nums;flex-shrink:0}
.fin-val.calc{color:var(--fin-calc)}.fin-val.ocr{color:var(--fin-ocr)}.fin-val.shop{color:var(--fin-shop)}
.fin-note{font-size:.68rem;color:var(--fg2);margin-top:8px}
.loading{color:var(--fg2);font-size:.83rem;padding:8px 0}
@media(max-width:480px){
  .room{width:46px;height:44px}
  .room .rn{font-size:.78rem}
  .kpi .n{font-size:1.4rem}
  .xnote{display:none}
  .dg{grid-template-columns:1fr 1fr}
}
</style>
</head>
<body>
<h1>🏨 บ้านเพื่อนรีสอร์ท — แผนที่ห้องพัก</h1>
<div style="display:flex;align-items:center;gap:8px;background:rgba(220,38,38,.12);border:1px solid rgba(220,38,38,.3);border-radius:8px;padding:8px 12px;margin-bottom:12px;font-size:.78rem">
  <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#ef4444;flex-shrink:0;animation:blink 1.5s infinite"></span>
  <span>เริ่มเก็บข้อมูลจริงตั้งแต่ <strong>30 ก.ย. 2569</strong> — ข้อมูลก่อนหน้านั้นอาจไม่สมบูรณ์</span>
</div>
<style>@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}</style>

<div class="quick-btns">
  <button class="qbtn" onclick="setRange(1)">วันนี้</button>
  <button class="qbtn" id="q7" onclick="setRange(7)">7 วัน</button>
  <button class="qbtn" onclick="setRange(14)">14 วัน</button>
  <button class="qbtn" onclick="setRange(30)">30 วัน</button>
</div>
<div class="controls">
  <input type="date" id="s">
  <span style="color:var(--fg2)">–</span>
  <input type="date" id="e">
  <button class="btn" onclick="load()">แสดง</button>
  <span class="loading" id="status"></span>
</div>

<div class="kpis">
  <div class="kpi"><div class="n" id="k1">—</div><div class="l">check-in ค้างคืน</div></div>
  <div class="kpi"><div class="n" id="k2">—</div><div class="l">check-in ชั่วคราว</div></div>
  <div class="kpi"><div class="n" id="k3">—</div><div class="l">ห้องพร้อม</div></div>
</div>

<div class="legend">
  <span style="font-weight:600;margin-right:2px">จำนวน check-in ในช่วงที่เลือก:</span>
  <span class="ls"><span class="lsw" style="background:var(--h0-bg);border:1px solid var(--border)"></span>0 (ไม่ถูกใช้)</span>
  <span class="ls"><span class="lsw" style="background:var(--h1-fg)"></span>1–5 ครั้ง</span>
  <span class="ls"><span class="lsw" style="background:var(--h2-fg)"></span>6–12 ครั้ง</span>
  <span class="ls"><span class="lsw" style="background:var(--h3-fg)"></span>13–20 ครั้ง</span>
  <span class="ls"><span class="lsw" style="background:var(--h4-fg)"></span>21+ ครั้ง</span>
</div>
<div class="legend" style="margin-top:-6px">
  <span style="font-weight:600;margin-right:2px">เส้นขอบ:</span>
  <span style="outline:2px dashed #f5a623;padding:1px 6px;border-radius:3px;font-size:.72rem">ย้ายออก</span>
  <span style="outline:2px dashed #34c066;padding:1px 6px;border-radius:3px;font-size:.72rem">ย้ายเข้า</span>
  <span style="font-size:.72rem;color:var(--fg2)">🔧 มีซ่อมบำรุง (ตัวเลขในห้อง = ค้างคืน + ชั่วคราว รวม)</span>
</div>

<!-- Building -->
<div class="sec-label">อาคาร 2 ชั้น (115–126)</div>
<div class="card">
  <div class="floor-tag">ชั้น 2</div>
  <div class="room-row" id="floor2"></div>
  <div class="floor-sep"></div>
  <div class="floor-tag">ชั้น 1</div>
  <div class="room-row" id="floor1"></div>
</div>

<!-- Bungalows -->
<div class="sec-label">วิลล่า รอบสวนกลาง (101–114)</div>
<div class="card">
  <div class="b-top" id="btop"></div>
  <div class="b-mid">
    <div class="b-col" id="bleft"></div>
    <div class="garden">🌳<br>สวนกลาง<br><span style="font-size:.65rem;opacity:.7">กดห้องเพื่อดูรายละเอียด</span></div>
    <div class="b-col" id="bright"></div>
  </div>
</div>

<!-- Detail panel -->
<div class="detail" id="detail" hidden>
  <h3 id="d-title">ห้อง —</h3>
  <div class="dg">
    <div class="ds"><div class="dn" id="d-ov">—</div><div class="dl">check-in ค้างคืน</div></div>
    <div class="ds"><div class="dn" id="d-tp">—</div><div class="dl">check-in ชั่วคราว</div></div>
    <div class="ds"><div class="dn" id="d-rd">—</div><div class="dl">ห้องพร้อม</div></div>
    <div class="ds"><div class="dn" id="d-co">—</div><div class="dl">check-out</div></div>
  </div>
  <div id="d-maint"></div>
  <div class="d-xfers" id="d-xfers"></div>
</div>

<!-- Financial panel -->
<div class="sec-label" style="margin-top:4px">ยอดเงิน (ประมาณการ)</div>
<div class="fin-panel">
  <div class="fin-row">
    <span class="fin-icon">🏨</span>
    <div><div class="fin-label">ค่าห้องที่คำนวณจากระบบ</div><div class="fin-sub">คำนวณจาก check-in × อัตราห้อง (ค้างคืน 500 / ชั่วคราว 180)</div></div>
    <div class="fin-val calc" id="f1">—</div>
  </div>
  <div class="fin-row">
    <span class="fin-icon">📷</span>
    <div><div class="fin-label">ยอดที่อ่านได้จาก OCR</div><div class="fin-sub">จากรูปสิ้นกะที่ถ่ายส่งในกลุ่ม</div></div>
    <div class="fin-val ocr" id="f2">—</div>
  </div>
  <div class="fin-row">
    <span class="fin-icon">🛒</span>
    <div><div class="fin-label">ค่าขายของ / ร้านค้า</div><div class="fin-sub">รายการขายของในรีสอร์ท</div></div>
    <div class="fin-val shop" id="f3">—</div>
  </div>
  <div class="fin-note">* ตัวเลขเป็นประมาณการ ไม่ใช่ยอดบัญชีจริง</div>
</div>

<!-- Transfer log -->
<div class="xlog-title">การย้ายห้อง</div>
<div id="xlog"></div>

<script>
// Physical layout — fixed (room numbers don't change)
const ZONES={
  floor2:["121","122","123","124","125","126"],
  floor1:["115","116","117","118","120"],
  btop:["110","109","108","107","106","105"],
  bleft:["111","112","113","114"],
  bright:["104","103","102","101"]
};
// Activity data — filled from API
const ROOMS={};
const MAINT={};
const XFERS=[];
const FINANCE={calc:null,ocr:null,shop:null};

// Initialise ROOMS with zero counts for every known room
const ALL_IDS=Object.values(ZONES).flat();
ALL_IDS.forEach(id=>{ROOMS[id]={ov:0,tp:0,rd:0,co:0};});

let sel=null;

function heatCss(total){
  if(total===0)return['var(--h0-bg)','var(--h0-fg)'];
  if(total<=5) return['var(--h1-bg)','var(--h1-fg)'];
  if(total<=12)return['var(--h2-bg)','var(--h2-fg)'];
  if(total<=20)return['var(--h3-bg)','var(--h3-fg)'];
  return            ['var(--h4-bg)','var(--h4-fg)'];
}
function fmt(n){return n===null||n===undefined?'ยังไม่มีข้อมูล':n.toLocaleString('th-TH')+'฿';}

function buildMap(){
  const xfFrom=new Set(XFERS.map(x=>x.from));
  const xfTo  =new Set(XFERS.map(x=>x.to));
  Object.entries(ZONES).forEach(([z,ids])=>{
    const el=document.getElementById(z);
    el.innerHTML='';
    ids.forEach(id=>{
      const d=ROOMS[id]||{ov:0,tp:0,rd:0,co:0};
      const tot=d.ov+d.tp;
      const[bg,fg]=heatCss(tot);
      const hasMaint=MAINT[id]&&MAINT[id].length>0;
      const div=document.createElement('div');
      div.className='room'+(xfFrom.has(id)?' xf-from':'')+(xfTo.has(id)?' xf-to':'')+(hasMaint?' has-maint':'');
      div.dataset.r=id;
      div.style.cssText='background:'+bg+';color:'+fg;
      div.innerHTML='<span class="rn">'+id+'</span><span class="rc">'+(tot||'—')+'</span>';
      div.addEventListener('click',()=>pick(id));
      el.appendChild(div);
    });
  });
}

function pick(id){
  if(sel)document.querySelector('.room[data-r="'+sel+'"]')?.classList.remove('selected');
  sel=id;
  document.querySelector('.room[data-r="'+id+'"]')?.classList.add('selected');
  const d=ROOMS[id]||{ov:0,tp:0,rd:0,co:0};
  const dp=document.getElementById('detail');
  dp.hidden=false;
  document.getElementById('d-title').textContent='ห้อง '+id;
  document.getElementById('d-ov').textContent=d.ov;
  document.getElementById('d-tp').textContent=d.tp;
  document.getElementById('d-rd').textContent=d.rd;
  document.getElementById('d-co').textContent=d.co;
  const mx=MAINT[id];
  const me=document.getElementById('d-maint');
  if(mx&&mx.length){
    me.innerHTML='<div class="d-maint"><div class="d-maint-title">🔧 ซ่อมบำรุงในช่วงนี้</div>'+
      mx.map(m=>'<span style="color:var(--fg2);font-size:.72rem">'+m.date+'</span> '+m.note).join('<br>')+
      '</div>';
  }else{me.innerHTML='';}
  const rx=XFERS.filter(x=>x.from===id||x.to===id);
  const xe=document.getElementById('d-xfers');
  xe.innerHTML=rx.length?rx.map(x=>{
    const dir=x.from===id
      ?'<span style="color:#f5a623">ย้ายออก → ห้อง '+x.to+'</span>'
      :'<span style="color:#34c066">ย้ายเข้า ← ห้อง '+x.from+'</span>';
    return x.date+' '+x.time+' · '+dir+' · <span style="color:var(--fg2)">'+x.note+'</span>';
  }).join('<br>'):'<span style="color:var(--fg2)">ไม่มีการย้ายห้องในช่วงนี้</span>';
  dp.scrollIntoView({behavior:'smooth',block:'nearest'});
}

function renderKPIs(){
  const all=Object.values(ROOMS);
  document.getElementById('k1').textContent=all.reduce((s,r)=>s+r.ov,0);
  document.getElementById('k2').textContent=all.reduce((s,r)=>s+r.tp,0);
  document.getElementById('k3').textContent=all.reduce((s,r)=>s+r.rd,0);
}

function renderFinance(){
  document.getElementById('f1').textContent=fmt(FINANCE.calc);
  document.getElementById('f2').textContent=fmt(FINANCE.ocr);
  document.getElementById('f3').textContent=fmt(FINANCE.shop);
}

function renderXLog(){
  document.getElementById('xlog').innerHTML=XFERS.length?XFERS.map(x=>`
    <div class="xfer">
      <span class="xdate">${x.date} ${x.time}</span>
      <div class="xarrow"><span class="xfrom">ห้อง ${x.from}</span><span style="color:var(--fg2)">→</span><span class="xto">ห้อง ${x.to}</span></div>
      <span class="xnote">${x.note}</span>
    </div>`).join(''):'<span style="color:var(--fg2);font-size:.8rem">ไม่มีการย้ายห้องในช่วงนี้</span>';
}

async function load(){
  const s=document.getElementById('s').value;
  const e=document.getElementById('e').value;
  const key=new URLSearchParams(location.search).get('key')||'';
  const st=document.getElementById('status');
  st.textContent='กำลังโหลด…';
  try{
    const r=await fetch('/api/roommap?start='+s+'&end='+e+'&key='+encodeURIComponent(key));
    if(!r.ok){st.textContent='ดึงข้อมูลไม่ได้ ('+r.status+')';return;}
    const d=await r.json();
    // Merge room activity
    ALL_IDS.forEach(id=>{
      const v=d.rooms&&d.rooms[id];
      ROOMS[id]=v?{ov:v.ov||0,tp:v.tp||0,rd:v.rd||0,co:v.co||0}:{ov:0,tp:0,rd:0,co:0};
    });
    // Maintenance
    Object.keys(MAINT).forEach(k=>delete MAINT[k]);
    if(d.maint)Object.assign(MAINT,d.maint);
    // Transfers
    XFERS.length=0;
    if(d.xfers)(d.xfers).forEach(x=>XFERS.push(x));
    // Finance
    if(d.finance){FINANCE.calc=d.finance.calc??null;FINANCE.ocr=d.finance.ocr??null;FINANCE.shop=d.finance.shop??null;}
    buildMap();renderKPIs();renderFinance();renderXLog();
    if(sel)pick(sel);
    st.textContent='';
  }catch(err){st.textContent='Error: '+err.message;}
}

function setRange(days){
  const e=new Date(),s=new Date();
  if(days>1)s.setDate(s.getDate()-(days-1));
  document.getElementById('e').value=e.toISOString().slice(0,10);
  document.getElementById('s').value=s.toISOString().slice(0,10);
  document.querySelectorAll('.qbtn').forEach(b=>b.classList.remove('active'));
  event.target.classList.add('active');
  load();
}

function initDates(){
  const e=new Date(),s=new Date();s.setDate(s.getDate()-6);
  document.getElementById('e').value=e.toISOString().slice(0,10);
  document.getElementById('s').value=s.toISOString().slice(0,10);
  document.getElementById('q7').classList.add('active');
}

initDates();load();
</script>
</body>
</html>"""
