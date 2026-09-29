WATER_HTML = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover">
<title>มิเตอร์น้ำ — บ้านเพื่อน</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap">
<style>
:root{
  --bg:#080c16;--surface:#101627;--surface2:#16203a;--border:#1f2e4a;
  --fg:#dde5f5;--fg2:#5f7299;--accent:#22a3d4;--accent2:#0ea5e9;
  color-scheme:dark;font-family:'Sarabun',system-ui,sans-serif;
}
@media(prefers-color-scheme:light){:root:not([data-theme="dark"]){
  --bg:#f0f7fc;--surface:#fff;--surface2:#e0eff8;--border:#b8d9ee;
  --fg:#0c1e2e;--fg2:#4a6e85;--accent:#0284c7;--accent2:#0369a1;
  color-scheme:light;
}}
:root[data-theme="light"]{
  --bg:#f0f7fc;--surface:#fff;--surface2:#e0eff8;--border:#b8d9ee;
  --fg:#0c1e2e;--fg2:#4a6e85;--accent:#0284c7;--accent2:#0369a1;
  color-scheme:light;
}
*,*::before,*::after{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);margin:0;padding:16px;padding-block:16px}
h1{font-size:1.05rem;font-weight:700;margin:0 0 12px;letter-spacing:.02em}
.notice{display:flex;align-items:center;gap:8px;background:rgba(220,38,38,.12);border:1px solid rgba(220,38,38,.3);border-radius:8px;padding:8px 12px;margin-bottom:12px;font-size:.78rem}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.dot{width:8px;height:8px;border-radius:50%;background:#ef4444;flex-shrink:0;animation:blink 1.5s infinite}
.quick-btns{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.qbtn{background:var(--surface2);color:var(--fg2);border:1px solid var(--border);padding:5px 12px;border-radius:20px;font:500 .78rem 'Sarabun',sans-serif;cursor:pointer;transition:background .1s,color .1s}
.qbtn:hover,.qbtn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:14px}
.controls input[type=date]{background:var(--surface);border:1px solid var(--border);color:var(--fg);padding:6px 9px;border-radius:6px;font:500 .83rem 'Sarabun',sans-serif}
.btn{background:var(--accent);color:#fff;border:none;padding:6px 14px;border-radius:6px;font:600 .83rem 'Sarabun',sans-serif;cursor:pointer}
.status{color:var(--fg2);font-size:.83rem}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:16px}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:10px 12px}
.kpi .n{font:700 1.7rem/1 'JetBrains Mono',monospace;font-variant-numeric:tabular-nums;color:var(--accent)}
.kpi .l{font-size:.68rem;color:var(--fg2);margin-top:3px}
.kpi.warn .n{color:#f59e0b}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 14px}
.card h3{font-size:.75rem;color:var(--fg2);margin:0 0 10px;text-transform:uppercase;letter-spacing:.06em}
.card canvas{max-height:220px}
.full{grid-column:1/-1}
.tbl{width:100%;border-collapse:collapse;font-size:.8rem;margin-top:2px}
.tbl th{color:var(--fg2);font-weight:600;text-align:left;padding:5px 8px;border-bottom:1px solid var(--border);font-size:.7rem;text-transform:uppercase;letter-spacing:.05em}
.tbl td{padding:6px 8px;border-bottom:1px solid var(--border)}
.tbl tr:last-child td{border-bottom:none}
.tbl .num{font-family:'JetBrains Mono',monospace;font-variant-numeric:tabular-nums;text-align:right}
.tbl .hi{color:#f59e0b}
.empty{color:var(--fg2);font-size:.85rem;padding:12px 0}
@media(max-width:520px){.grid{grid-template-columns:1fr}.kpi .n{font-size:1.3rem}}
</style>
</head>
<body>
<h1>💧 มิเตอร์น้ำ — บ้านเพื่อนรีสอร์ท</h1>

<div class="notice">
  <span class="dot"></span>
  <span>เริ่มเก็บข้อมูลจริงตั้งแต่ <strong>30 ก.ย. 2569</strong> — ข้อมูลก่อนหน้านั้นอาจไม่สมบูรณ์</span>
</div>

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
  <span class="status" id="status"></span>
</div>

<div class="kpis">
  <div class="kpi"><div class="n" id="k1">—</div><div class="l">เลขมิเตอร์ล่าสุด (หน่วย)</div></div>
  <div class="kpi warn"><div class="n" id="k2">—</div><div class="l">การใช้รวมในช่วงนี้ (หน่วย)</div></div>
  <div class="kpi"><div class="n" id="k3">—</div><div class="l">บันทึกที่พบ</div></div>
</div>

<div class="grid">
  <div class="card full"><h3>เลขมิเตอร์รายวัน</h3><canvas id="cReading"></canvas></div>
  <div class="card full"><h3>การใช้น้ำต่อวัน (หน่วย)</h3><canvas id="cConsume"></canvas></div>
  <div class="card full">
    <h3>บันทึกทั้งหมด</h3>
    <div id="tblWrap"><div class="empty">กำลังโหลด…</div></div>
  </div>
</div>

<script>
const ci={};
function mk(id,cfg){if(ci[id])ci[id].destroy();ci[id]=new Chart(document.getElementById(id),cfg)}
const gc=()=>({x:{ticks:{color:'#5f7299',font:{size:10}},grid:{color:'#1f2e4a'}},y:{ticks:{color:'#5f7299',font:{size:10}},grid:{color:'#1f2e4a'},beginAtZero:false}})

function setRange(days){
  const e=new Date(),s=new Date();
  if(days>1)s.setDate(s.getDate()-(days-1));
  document.getElementById('e').value=e.toISOString().slice(0,10);
  document.getElementById('s').value=s.toISOString().slice(0,10);
  document.querySelectorAll('.qbtn').forEach(b=>b.classList.remove('active'));
  event.target.classList.add('active');
  load();
}

async function load(){
  const s=document.getElementById('s').value,e=document.getElementById('e').value;
  const key=new URLSearchParams(location.search).get('key')||'';
  const st=document.getElementById('status');
  st.textContent='กำลังโหลด…';
  try{
    const r=await fetch('/api/water?start='+s+'&end='+e+'&key='+encodeURIComponent(key));
    if(!r.ok){st.textContent='ดึงข้อมูลไม่ได้ ('+r.status+')';return;}
    const d=await r.json();
    const sm=d.summary||{};
    document.getElementById('k1').textContent=sm.latest!=null?sm.latest.toLocaleString('th-TH'):'—';
    document.getElementById('k2').textContent=sm.total_consumption!=null?sm.total_consumption.toLocaleString('th-TH'):'—';
    document.getElementById('k3').textContent=sm.count??'0';

    const dl=d.daily||[];
    if(dl.length){
      mk('cReading',{type:'line',data:{
        labels:dl.map(x=>x.date.slice(5)),
        datasets:[{
          label:'เลขมิเตอร์',data:dl.map(x=>x.reading),
          borderColor:'#22a3d4',backgroundColor:'rgba(34,163,212,.1)',
          tension:.3,fill:true,pointRadius:4,pointBackgroundColor:'#22a3d4'
        }]
      },options:{plugins:{legend:{labels:{color:'#dde5f5',font:{size:11}}}},scales:gc()}});

      const cData=dl.map(x=>x.consumption);
      mk('cConsume',{type:'bar',data:{
        labels:dl.map(x=>x.date.slice(5)),
        datasets:[{
          label:'การใช้น้ำ (หน่วย)',
          data:cData,
          backgroundColor:cData.map(v=>v==null?'#1f2e4a':v>5?'#f59e0b':'#22a3d4'),
          borderRadius:3
        }]
      },options:{
        plugins:{legend:{labels:{color:'#dde5f5',font:{size:11}}}},
        scales:{
          x:{ticks:{color:'#5f7299',font:{size:10}},grid:{color:'#1f2e4a'}},
          y:{ticks:{color:'#5f7299',font:{size:10}},grid:{color:'#1f2e4a'},beginAtZero:true}
        }
      }});
    }else{
      ['cReading','cConsume'].forEach(id=>{
        const ctx=document.getElementById(id).getContext('2d');
        ctx.fillStyle='#5f7299';ctx.font='13px Sarabun';
        ctx.fillText('ไม่มีข้อมูลในช่วงนี้ — ข้อความในกลุ่มที่มีคำว่า "มิเตอร์" จะถูกบันทึก',16,40);
      });
    }

    const wrap=document.getElementById('tblWrap');
    if(d.readings&&d.readings.length){
      wrap.innerHTML='<table class="tbl"><thead><tr><th>วันที่</th><th>เวลา</th><th>เลขมิเตอร์</th><th>ผู้บันทึก</th><th>ข้อความ</th></tr></thead><tbody>'+
        d.readings.slice().reverse().map(x=>`<tr>
          <td>${x.date}</td><td>${x.time}</td>
          <td class="num">${x.value.toLocaleString('th-TH')}</td>
          <td style="color:var(--fg2)">${x.user}</td>
          <td style="color:var(--fg2);font-size:.72rem">${x.note}</td>
        </tr>`).join('')+
        '</tbody></table>';
    }else{
      wrap.innerHTML='<div class="empty">ยังไม่มีบันทึกมิเตอร์น้ำ — พิมพ์ "มิเตอร์ XXXX" ในกลุ่ม LINE</div>';
    }
    st.textContent='';
  }catch(err){st.textContent='Error: '+err.message;}
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
