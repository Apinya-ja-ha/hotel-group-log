DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Hotel Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#e6edf3;font-family:'Segoe UI',sans-serif;padding:16px;min-height:100vh}
h1{font-size:1.3rem;margin-bottom:14px;color:#fff}
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:18px}
.controls input[type=date]{background:#161b22;border:1px solid #30363d;color:#e6edf3;
  padding:7px 10px;border-radius:8px;font-size:.9rem}
.controls button{background:#238636;color:#fff;border:none;padding:7px 18px;
  border-radius:8px;cursor:pointer;font-size:.9rem;font-weight:600}
.controls button:hover{background:#2ea043}
.kpi-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:18px}
.kpi{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:14px;text-align:center}
.kpi .val{font-size:1.9rem;font-weight:700}
.kpi .lbl{font-size:.75rem;color:#8b949e;margin-top:4px}
.kpi.blue .val{color:#58a6ff}
.kpi.green .val{color:#3fb950}
.kpi.orange .val{color:#d29922}
.kpi.purple .val{color:#bc8cff}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:14px}
.card h3{font-size:.82rem;color:#8b949e;margin-bottom:10px;text-transform:uppercase;letter-spacing:.05em}
.card canvas{max-height:250px}
.full{grid-column:1/-1}
.note{font-size:.72rem;color:#6e7681;margin-top:6px}
@media(max-width:560px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<h1>🏨 Hotel Dashboard</h1>
<div class="controls">
  <input type="date" id="s">
  <span style="color:#8b949e">ถึง</span>
  <input type="date" id="e">
  <button onclick="load()">แสดง</button>
</div>
<div class="kpi-row">
  <div class="kpi blue"><div class="val" id="k1">—</div><div class="lbl">check-in รวม</div></div>
  <div class="kpi green"><div class="val" id="k2">—</div><div class="lbl">check-out รวม</div></div>
  <div class="kpi orange"><div class="val" id="k3">—</div><div class="lbl">ห้องพร้อม</div></div>
  <div class="kpi purple"><div class="val" id="k4">—</div><div class="lbl">ข้อความทั้งหมด</div></div>
</div>
<div class="grid">
  <div class="card full"><h3>กิจกรรมรายวัน</h3><canvas id="cDaily"></canvas></div>
  <div class="card"><h3>ตามชั่วโมง</h3><canvas id="cHour"></canvas></div>
  <div class="card"><h3>สัดส่วนประเภท</h3><canvas id="cCat"></canvas></div>
  <div class="card full">
    <h3>ห้องที่มีกิจกรรมบ่อย</h3>
    <canvas id="cRoom"></canvas>
    <div class="note">* ตัวเลขเป็นประมาณการจากข้อความในกลุ่ม</div>
  </div>
</div>
<script>
const ci={};
function mk(id,cfg){if(ci[id])ci[id].destroy();ci[id]=new Chart(document.getElementById(id),cfg)}
const gc=(v)=>({x:{ticks:{color:'#8b949e',font:{size:10}},grid:{color:'#21262d'}},
  y:{ticks:{color:'#8b949e',font:{size:10}},grid:{color:'#21262d'},beginAtZero:true},...v})

function initDates(){
  const e=new Date(),s=new Date();s.setDate(s.getDate()-6);
  document.getElementById('e').value=e.toISOString().slice(0,10);
  document.getElementById('s').value=s.toISOString().slice(0,10);
}
async function load(){
  const s=document.getElementById('s').value,e=document.getElementById('e').value;
  const key=new URLSearchParams(location.search).get('key')||'';
  const r=await fetch(`/api/data?start=${s}&end=${e}&key=${encodeURIComponent(key)}`);
  if(!r.ok){alert('ดึงข้อมูลไม่ได้ ('+r.status+')');return;}
  const d=await r.json();
  const sm=d.summary||{};
  document.getElementById('k1').textContent=sm.total_checkin??'0';
  document.getElementById('k2').textContent=sm.total_checkout??'0';
  document.getElementById('k3').textContent=sm.total_room_ready??'0';
  document.getElementById('k4').textContent=sm.total_messages??'0';

  const dl=d.daily||[];
  mk('cDaily',{type:'line',data:{
    labels:dl.map(x=>x.date.slice(5)),
    datasets:[
      {label:'check-in ค้างคืน',data:dl.map(x=>x['check-in ค้างคืน']),borderColor:'#58a6ff',tension:.3,fill:false,pointRadius:4},
      {label:'check-in ชั่วคราว',data:dl.map(x=>x['check-in ชั่วคราว']),borderColor:'#3fb950',tension:.3,fill:false,pointRadius:4},
      {label:'check-out',data:dl.map(x=>x['check-out']),borderColor:'#d29922',tension:.3,fill:false,pointRadius:4},
      {label:'ห้องพร้อม',data:dl.map(x=>x['ห้องพร้อม']),borderColor:'#bc8cff',tension:.3,fill:false,pointRadius:4},
    ]
  },options:{plugins:{legend:{labels:{color:'#e6edf3',font:{size:11},boxWidth:14}}},scales:gc({})}});

  const hr=d.hourly||[];
  mk('cHour',{type:'bar',data:{
    labels:hr.map((_,i)=>i+':00'),
    datasets:[{data:hr,backgroundColor:hr.map((_,i)=>(i>=8&&i<17)?'#58a6ff':'#30363d'),borderRadius:3}]
  },options:{plugins:{legend:{display:false}},scales:gc({x:{ticks:{color:'#8b949e',font:{size:8},maxRotation:0}}})}});

  const cats=d.categories||{};
  const ce=Object.entries(cats).sort((a,b)=>b[1]-a[1]);
  const pal=['#58a6ff','#3fb950','#d29922','#bc8cff','#f85149','#1f6feb','#388bfd','#8b949e'];
  mk('cCat',{type:'doughnut',data:{
    labels:ce.map(e=>e[0]),
    datasets:[{data:ce.map(e=>e[1]),backgroundColor:pal,borderWidth:0}]
  },options:{plugins:{legend:{position:'right',labels:{color:'#e6edf3',font:{size:10},boxWidth:12,padding:8}}}}});

  const rm=d.rooms||{};
  const re=Object.entries(rm).slice(0,15);
  if(re.length>0){
    mk('cRoom',{type:'bar',data:{
      labels:re.map(e=>'ห้อง '+e[0]),
      datasets:[{data:re.map(e=>e[1]),backgroundColor:'#58a6ff',borderRadius:4}]
    },options:{indexAxis:'y',plugins:{legend:{display:false}},scales:gc({y:{ticks:{color:'#e6edf3',font:{size:11}}}})}});
  } else {
    const ctx=document.getElementById('cRoom').getContext('2d');
    ctx.fillStyle='#8b949e';ctx.font='14px Segoe UI';
    ctx.fillText('ยังไม่มีข้อมูลห้อง (ตรวจสอบว่าข้อความมีเลขห้องไหม)',20,40);
  }
}
initDates();load();
</script>
</body>
</html>"""
