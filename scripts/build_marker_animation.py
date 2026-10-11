from pathlib import Path
import json
import numpy as np
import ezc3d

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
c3d_path = (
    project / "openbiomechanics" / "baseball_pitching" / "data" /
    "c3d" / "000002" / "000002_003034_73_207_002_FF_809.c3d"
)
output_path = project / "outputs" / "pitch_marker_animation.html"
output_path.parent.mkdir(parents=True, exist_ok=True)

print("Reading C3D:", c3d_path)
c3d = ezc3d.c3d(str(c3d_path))

labels = [
    str(x).strip()
    for x in c3d["parameters"]["POINT"]["LABELS"]["value"]
]
points = np.asarray(c3d["data"]["points"], dtype=float)
rate = float(c3d["header"]["points"]["frame_rate"])

# ezc3d point array: coordinate x marker x frame.
xyz = points[:3, :, :].transpose(2, 1, 0)

# Convert laboratory Z-up into a right-handed Y-up display convention.
# Display coordinates: [x, z, -y].
xyz = xyz[:, :, [0, 2, 1]]
xyz[:, :, 2] *= -1

# Use the overall trajectory center so the full pitch remains in view.
valid = np.isfinite(xyz).all(axis=2)
if not valid.all():
    print("Warning: missing marker samples will be omitted from display.")

xyz = np.nan_to_num(xyz, nan=0.0, posinf=0.0, neginf=0.0)
frames = xyz.tolist()

# Connect available measured landmarks into an approximate stick figure.
edges = [
    ("C7", "CLAV"), ("CLAV", "STRN"), ("STRN", "T10"),
    ("T10", "LPSI"), ("T10", "RPSI"),
    ("LASI", "RASI"), ("LASI", "LPSI"), ("RASI", "RPSI"),
    ("CLAV", "LSHO"), ("LSHO", "LUPA"), ("LUPA", "LELB"),
    ("LELB", "LMELB"), ("LELB", "LFRM"), ("LFRM", "LWRA"),
    ("LWRA", "LWRB"), ("LWRA", "LFIN"),
    ("CLAV", "RSHO"), ("RSHO", "RUPA"), ("RUPA", "RELB"),
    ("RELB", "RMELB"), ("RELB", "RFRM"), ("RFRM", "RWRA"),
    ("RWRA", "RWRB"), ("RWRA", "RFIN"),
    ("LASI", "LTHI"), ("LTHI", "LKNE"), ("LKNE", "LMKNE"),
    ("LKNE", "LTIB"), ("LTIB", "LANK"), ("LANK", "LMANK"),
    ("LANK", "LHEE"), ("LHEE", "LTOE"),
    ("RASI", "RTHI"), ("RTHI", "RKNE"), ("RKNE", "RMKNE"),
    ("RKNE", "RTIB"), ("RTIB", "RANK"), ("RANK", "RMANK"),
    ("RANK", "RHEE"), ("RHEE", "RTOE"),
]
index = {name: i for i, name in enumerate(labels)}
edges = [[index[a], index[b]] for a, b in edges
         if a in index and b in index]

payload = {
    "labels": labels,
    "frames": frames,
    "edges": edges,
    "rate": rate,
    "units": str(c3d["parameters"]["POINT"]["UNITS"]["value"][0]),
    "valid": valid.tolist(),
}

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Baseball Pitch — 3D Marker Animation</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#10151d;color:#edf2f7;font:14px system-ui,Segoe UI,sans-serif}
header{padding:14px 20px;background:#1b2430;border-bottom:1px solid #344153}
h1{font-size:19px;margin:0 0 5px}
p{margin:4px 0;color:#b9c5d4}
main{padding:12px;max-width:1500px;margin:auto}
#stage{height:min(68vh,720px);min-height:390px;background:#0b1017;border:1px solid #344153;border-radius:10px;overflow:hidden}
canvas{width:100%;height:100%;display:block;touch-action:none}
.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:12px 0}
button,select,input{accent-color:#61a5fa}
button,select{background:#202b39;color:#edf2f7;border:1px solid #48576a;border-radius:6px;padding:8px 12px}
button{cursor:pointer}
#timeline{flex:1;min-width:180px}
#time{font-variant-numeric:tabular-nums;min-width:115px}
small{color:#9fadc0}
</style>
</head>
<body>
<header>
<h1>Baseball Pitch — 3D Marker Animation</h1>
<p>Measured motion-capture markers · 360 Hz · Coordinate display: Y-up</p>
</header>
<main>
<div id="stage"><canvas id="view"></canvas></div>
<div class="controls">
<button id="play">Play</button>
<button id="reset">Reset view</button>
<label>Frame <input id="timeline" type="range" min="0" max="725" value="0"></label>
<span id="time">0.0000 s</span>
<label>Speed
<select id="speed"><option value=".25">0.25×</option><option value=".5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select>
</label>
<label><input id="showLabels" type="checkbox" checked> Marker labels</label>
<label><input id="showLines" type="checkbox" checked> Stick figure</label>
</div>
<p id="info"></p>
<small>Drag to rotate · Scroll to zoom · Stick connections are approximate visual guides, not fitted anatomical joints.</small>
</main>
<script>
const D = __DATA__;
const canvas = document.getElementById('view');
const ctx = canvas.getContext('2d');
const timeline = document.getElementById('timeline');
const timeLabel = document.getElementById('time');
const playButton = document.getElementById('play');
const labelToggle = document.getElementById('showLabels');
const lineToggle = document.getElementById('showLines');
timeline.max = D.frames.length - 1;
document.getElementById('info').textContent =
  `${D.labels.length} markers · ${D.frames.length} frames · ${D.units} · ` +
  `${((D.frames.length-1)/D.rate).toFixed(4)} s`;

let frame = 0, playing = false, last = 0, accumulator = 0;
let yaw = -0.65, pitch = 0.12, zoom = 1, dragging = false, px = 0, py = 0;

const all = D.frames.flat().filter(p => p.every(Number.isFinite));
const center = [0,1,2].map(k => all.reduce((s,p)=>s+p[k],0)/all.length);
let extent = 0;
for (const p of all) extent = Math.max(extent, ...p.map((v,k)=>Math.abs(v-center[k])));
extent = Math.max(extent, 0.1);

function resize(){
  const r = canvas.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
  canvas.width = Math.round(r.width*dpr);
  canvas.height = Math.round(r.height*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
  draw();
}
function project(p,w,h){
  let x=p[0]-center[0], y=p[1]-center[1], z=p[2]-center[2];
  const ca=Math.cos(yaw), sa=Math.sin(yaw);
  const xx=ca*x-sa*z, zz=sa*x+ca*z;
  const cb=Math.cos(pitch), sb=Math.sin(pitch);
  const yy=cb*y-sb*zz, depth=sb*y+cb*zz;
  const scale=Math.min(w,h)*0.43/extent*zoom;
  return {x:w/2+xx*scale,y:h/2-yy*scale,z:depth};
}
function draw(){
  const w=canvas.clientWidth,h=canvas.clientHeight;
  if(!w||!h)return;
  ctx.clearRect(0,0,w,h);
  ctx.fillStyle='#0b1017';ctx.fillRect(0,0,w,h);
  // Ground-plane grid, centered at the trajectory origin.
  ctx.lineWidth=1;ctx.strokeStyle='#1e2a38';
  for(let i=-4;i<=4;i++){
    const a=project([center[0]+i*extent/4,center[1]-center[1],center[2]-extent],w,h);
    const b=project([center[0]+i*extent/4,center[1]-center[1],center[2]+extent],w,h);
    const c=project([center[0]-extent,0,center[2]+i*extent/4],w,h);
    const d=project([center[0]+extent,0,center[2]+i*extent/4],w,h);
    ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
    ctx.beginPath();ctx.moveTo(c.x,c.y);ctx.lineTo(d.x,d.y);ctx.stroke();
  }
  // Coordinate axes: X red, Y green (up), Z blue.
  const axes=[[[1,0,0],'#f87171'],[[0,1,0],'#4ade80'],[[0,0,1],'#60a5fa']];
  for(const [v,col] of axes){
    const a=project(center,w,h),b=project(center.map((x,i)=>x+v[i]*extent*.45),w,h);
    ctx.strokeStyle=col;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
    ctx.fillStyle=col;ctx.fillText(['X','Y','Z'][axes.findIndex(x=>x[0]===v)],b.x+4,b.y-4);
  }
  const pts=D.frames[frame].map(p=>project(p,w,h));
  if(lineToggle.checked){
    ctx.lineWidth=2;ctx.strokeStyle='#8394aa';
    for(const [a,b] of D.edges){
      if(!D.valid[frame][a]||!D.valid[frame][b])continue;
      ctx.beginPath();ctx.moveTo(pts[a].x,pts[a].y);ctx.lineTo(pts[b].x,pts[b].y);ctx.stroke();
    }
  }
  const order=pts.map((p,i)=>({p,i})).sort((a,b)=>a.p.z-b.p.z);
  for(const {p,i} of order){
    if(!D.valid[frame][i])continue;
    ctx.beginPath();ctx.arc(p.x,p.y,3.5,0,Math.PI*2);
    ctx.fillStyle='#fbbf24';ctx.fill();
    if(labelToggle.checked){
      ctx.font='10px system-ui';ctx.fillStyle='#dbe5f0';
      ctx.fillText(D.labels[i],p.x+5,p.y-4);
    }
  }
  timeLabel.textContent=(frame/D.rate).toFixed(4)+' s';
  timeline.value=frame;
}
function animate(ts){
  if(playing){
    if(!last)last=ts;
    accumulator+=(ts-last)*Number(document.getElementById('speed').value);
    last=ts;
    const interval=1000/D.rate;
    while(accumulator>=interval){
      frame=(frame+1)%D.frames.length;accumulator-=interval;
    }
    draw();
  }else last=0;
  requestAnimationFrame(animate);
}
playButton.onclick=()=>{playing=!playing;playButton.textContent=playing?'Pause':'Play';};
document.getElementById('reset').onclick=()=>{yaw=-0.65;pitch=0.12;zoom=1;draw();};
timeline.oninput=()=>{frame=Number(timeline.value);draw();};
labelToggle.onchange=draw;lineToggle.onchange=draw;
canvas.addEventListener('pointerdown',e=>{dragging=true;px=e.clientX;py=e.clientY;canvas.setPointerCapture(e.pointerId);});
canvas.addEventListener('pointerup',()=>dragging=false);
canvas.addEventListener('pointermove',e=>{
  if(!dragging)return;
  yaw+=(e.clientX-px)*0.008;pitch=Math.max(-1.5,Math.min(1.5,pitch+(e.clientY-py)*0.008));
  px=e.clientX;py=e.clientY;draw();
});
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.4,Math.min(4,zoom*(e.deltaY>0?.9:1.1)));draw();},{passive:false});
window.addEventListener('resize',resize);
resize();requestAnimationFrame(animate);
</script>
</body></html>'''

html = html.replace("__DATA__", json.dumps(payload, separators=(",", ":")))
output_path.write_text(html, encoding="utf-8")

print("\nCreated:", output_path)
print("Frames:", len(frames))
print("Markers:", len(labels))
print("Rate:", rate, "Hz")
print("Duration:", f"{(len(frames)-1)/rate:.4f}", "seconds")
print("Skeletal connections:", len(edges))
print("Open the HTML file in your browser to play the animation.")
