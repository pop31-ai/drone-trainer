const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const htmlPath = path.join(__dirname, '..', 'index.html');
const src = fs.readFileSync(htmlPath, 'utf8');

const i0 = src.indexOf('const AR = 0.225;');
const i1 = src.indexOf('function syncDroneMesh');
if (i0 < 0 || i1 < 0 || i1 <= i0) {
  console.error('EXTRA: markers "const AR = 0.225;" / "function syncDroneMesh" not found in index.html');
  process.exit(2);
}
const chunk = src.slice(i0, i1);

const stub = `
class V3 { constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
  set(x,y,z){this.x=x;this.y=y;this.z=z;return this;}
  clone(){return new V3(this.x,this.y,this.z);}
  add(o){this.x+=o.x;this.y+=o.y;this.z+=o.z;return this;}
  sub(o){this.x-=o.x;this.y-=o.y;this.z-=o.z;return this;}
  addScaledVector(o,s){this.x+=o.x*s;this.y+=o.y*s;this.z+=o.z*s;return this;}
  multiplyScalar(s){this.x*=s;this.y*=s;this.z*=s;return this;}
  divideScalar(s){this.x/=s;this.y/=s;this.z/=s;return this;}
  normalize(){const l=this.length()||1;this.x/=l;this.y/=l;this.z/=l;return this;}
  length(){return Math.hypot(this.x,this.y,this.z);}
  clampLength(min,max){const l=this.length();if(l>0&&l<min)this.multiplyScalar(min/l);else if(l>max)this.multiplyScalar(max/l);return this;}
  cross(o){return new V3(this.y*o.z-this.z*o.y,this.z*o.x-this.x*o.z,this.x*o.y-this.y*o.x);}
  applyQuaternion(q){const x=this.x,y=this.y,z=this.z;const qx=q.x,qy=q.y,qz=q.z,qw=q.w;
    const ix= qw*x+qy*z-qz*y, iy= qw*y+qz*x-qx*z, iz= qw*z+qx*y-qy*x, iw=-qx*x-qy*y-qz*z;
    this.x= ix*qw+iw*-qx+iy*-qz-iz*-qy;
    this.y= iy*qw+iw*-qy+iz*-qx-ix*-qz;
    this.z= iz*qw+iw*-qz+ix*-qy-iy*-qx;
    return this; } }
class Quat { constructor(){this.x=0;this.y=0;this.z=0;this.w=1;}
  set(x,y,z,w){this.x=x;this.y=y;this.z=z;this.w=w;return this;}
  clone(){return new Quat().set(this.x,this.y,this.z,this.w);}
  conjugate(){this.x=-this.x;this.y=-this.y;this.z=-this.z;return this;}
  invert(){this.x=-this.x;this.y=-this.y;this.z=-this.z;return this;}
  multiply(o){const a=this,b=o;
    const x=a.x*b.w+a.y*b.z-a.z*b.y+a.w*b.x;
    const y=-a.x*b.z+a.y*b.w+a.z*b.x+a.w*b.y;
    const z= a.x*b.y-a.y*b.x+a.z*b.w+a.w*b.z;
    const w=-a.x*b.x-a.y*b.y-a.z*b.z+a.w*b.w;
    this.set(x,y,z,w);return this;}
  normalize(){const l=Math.hypot(this.x,this.y,this.z,this.w)||1;
    this.x/=l;this.y/=l;this.z/=l;this.w/=l;return this;}
  setFromAxisAngle(axis,ang){const h=ang/2,s=Math.sin(h);
    this.x=axis.x*s;this.y=axis.y*s;this.z=axis.z*s;this.w=Math.cos(h);return this;} }
const THREE={Vector3:V3,Quaternion:Quat};
function clamp(v,a,b){return Math.max(a,Math.min(b,v));}
`;

const tail = `
const FIX=1/240, FPS=1/60; let dtRender=FPS;
const gates=[], obstacles=[];
function addGate(x,y,z,rotY){gates.push({x,y,z,rotY,passed:false});}
const PROGS=[
 {name:'Круг',gates:[[20,5,0,0],[10,5,14,Math.PI/2],[-10,5,14,Math.PI/2],[-20,5,0,0],[-10,5,-14,-Math.PI/2],[10,5,-14,-Math.PI/2]]},
 {name:'Квадрат',gates:[[18,4,0,0],[18,5,16,Math.PI/2],[-8,6,16,Math.PI/2],[-8,4,0,0]]},
 {name:'Спираль',gates:[[20,3,0,0],[8,4,20,Math.PI/2.2],[-12,5,-6,Math.PI/5],[0,7,-20,-Math.PI/2.2],[6,8,4,Math.PI/4]]},
];
const M={tasks:[],current:0,done:false,name:''};
function checkGateNow(){
  for(const g of gates){
    if(g.passed) continue;
    const nx=Math.sin(g.rotY), nz=Math.cos(g.rotY);
    const dx=S.pos.x-g.x, dz=S.pos.z-g.z;
    const perp=Math.abs(dx*nx+dz*nz), lat=Math.abs(dx*(-Math.cos(g.rotY))+dz*Math.sin(g.rotY));
    const rad=Math.hypot(S.pos.y-g.y, lat);
    if(perp<0.9 && rad<2.0){ g.passed=true; }
    else if(perp<0.85 && rad<2.5 && rad>2.0){
      S.state='crash'; S.crashMsg='КАСАНИЕ КОЛЬЦА'; S.hardHit=true;
      console.log('  <touch> pos',S.pos.x.toFixed(2),S.pos.y.toFixed(2),S.pos.z.toFixed(2),'gate',g.x,g.y,g.z,'perp',perp.toFixed(2),'lat',lat.toFixed(2),'rad',rad.toFixed(2),'vy',S.vel.y.toFixed(2),'spd',Math.hypot(S.vel.x,S.vel.z).toFixed(2));
      return;
    }
  }
}
let won=false;
function checkMissionNow(){
  const tk=M.tasks[M.current];
  if(!tk){ won=true; return; }
  if(S.state!=='mission') return;
  if(typeof tk.timer==='number'){ if(!tk._t)tk._t=0; if(tk.ok())tk._t+=FPS; else tk._t=0; if(tk._t>=tk.timer){M.current++; if(M.current>=M.tasks.length)won=true;} }
  else if(tk.ok()){ M.current++; }
}
function checkFallsNow(){
  if(S.state==='crash'||S.state==='lost')return;
  const e=eulFromQuat(S.quat);
  if(S.hardHit && S.pos.y<=0.05){S.state='crash';S.crashMsg='КРУШЕНИЕ О ЗЕМЛЮ';return;}
  if(S.pos.y<0.25 && Math.max(Math.abs(e.phi),Math.abs(e.theta))>0.8){S.state='crash';S.crashMsg='ПЕРЕВОРОТ';return;}
  if(Math.hypot(S.pos.x,S.pos.z)>95){S.state='lost';S.crashMsg='ЗОНА';return;}
  for(const o of obstacles){
    const dx=S.pos.x-o.x, dy=Math.max(0,S.pos.y-o.y), dz=S.pos.z-o.z;
    if(dx*dx+dy*dy+dz*dz < o.r*o.r){ S.state='crash'; S.crashMsg='СТОЛКНОВЕНИЕ'; return; }
  }
}
function resetFor(missIdx, progIdx, pil){
  S.pos.set(0,0.04,0); S.vel.set(0,0,0); S.ang.set(0,0,0); S.quat.set(0,0,0,1);
  S.motor=[0,0,0,0]; S.motorOut=[0,0,0,0]; S.batt=1; S.armed=false; S.state='mission'; S.hardHit=false; S.ih=0;
  gates.length=0; obstacles.length=0;
  PILOT=pil; AI_h=0; AI_g=null; AI_dir=null; AI_cv={u:0,v:0,on:false,dist:999};
  if(missIdx>=0){
    S.mActive=missIdx;
    if(missIdx===0){ M.tasks=[
      {t:'0. Вооружить', ok:()=>S.armed},
      {t:'1. Взлететь', ok:()=>S.pos.y>=2},
      {t:'2. Держать 4м', ok:()=>S.pos.y>=3.2&&S.pos.y<=4.8&&S.state!=='crash', timer:4},
      {t:'4. Мягко приземлиться (пасс: |Vy|<1.2)', ok:()=>S.pos.y<0.2&&Math.abs(S.vel.y)<1.2, timer:2, safeLand:true}];
    }
    else if(missIdx===2){ M.tasks=[
      {t:'0. Взлететь', ok:()=>S.pos.y>=5},
      {t:'1. Над центром', ok:()=>Math.hypot(S.pos.x,S.pos.z)<2, timer:3},
      {t:'3. Мягкая посадка на ПОДИУМ', ok:()=>S.pos.y<0.22&&Math.abs(S.vel.y)<1.0&&Math.hypot(S.pos.x,S.pos.z)<2.2, timer:2, safeLand:true}];
    }
    else {
      M.tasks=[{t:'0. Взлететь', ok:()=>S.pos.y>=2}];
      if(missIdx===1){addGate(16,6,0,0);addGate(32,6,10,Math.PI/2.4);addGate(50,8,-4,Math.PI/6);}
      if(missIdx===3){addGate(18,3,0,0);addGate(14,4,18,Math.PI/2);addGate(40,6,18,0);addGate(-6,2,18,Math.PI/2);
        obstacles.push({x:24,y:1.6,z:6,r:1.6},{x:30,y:1.2,z:-6,r:1.8},{x:2,y:1.5,z:16,r:2.0});}
      gates.forEach((g,i)=>M.tasks.push({t:(i+1), ok:()=>gates[i].passed}));
    }
  } else {
    S.mActive=4; const p=PROGS[progIdx];
    M.tasks=[{t:'0. Взлететь', ok:()=>S.pos.y>=2}];
    p.gates.forEach(g=>addGate(g[0],g[1],g[2],g[3]));
    gates.forEach((g,i)=>M.tasks.push({t:(i+1), ok:()=>gates[i].passed}));
  }
  M.current=0; M.done=false; won=false;
}
function runSim(name, timeout, missIdx, progIdx, pil, wind){
  resetFor(missIdx, progIdx, pil);
  const nFrames=Math.round(timeout/FPS);
  let acc=0, armed=false, t=0;
  for(let f=0; f<nFrames; f++){
    t=f*FPS;
    if(wind===1) S.wind.set(1.6+0.6*Math.sin(t*0.7), 0, 0.5+0.4*Math.sin(t*0.5));
    else if(wind===2) S.wind.set(4.5+1.8*Math.sin(t*0.9), 0, 1.2+1.1*Math.sin(t*0.63));
    else if(!wind) S.wind.set(0,0,0);
    acc+=FPS; let steps=0;
    while(acc>=FIX && steps<10){ physicsStep(FIX); acc-=FIX; steps++; }
    if(steps>=10)acc=0;
    if(PILOT>0 && S.state==='mission'){ armed=true; S.armed=true; }
    const st=aiPilotSticks();
    CTRL.throttle=clamp((st.L.y+1)/2,0,1); CTRL.yawS=st.L.x; CTRL.pitchS=st.R.y; CTRL.rollS=st.R.x;
    checkGateNow(); checkMissionNow(); checkFallsNow();
    if(S.state==='crash') return name+' crash:'+S.crashMsg+' @'+ (f*FPS).toFixed(0)+'s pos='+S.pos.x.toFixed(1)+','+S.pos.y.toFixed(1)+','+S.pos.z.toFixed(1);
    if(S.state==='lost') return name+' lost:'+S.crashMsg+' @'+ (f*FPS).toFixed(0)+'s';
    if(won) return name+' WIN '+ (f*FPS).toFixed(1)+'s gates='+gates.filter(g=>g.passed).length+' y='+S.pos.y.toFixed(2);
  }
  return name+' TIMEOUT gates='+gates.filter(g=>g.passed).length+' pos='+S.pos.x.toFixed(0)+','+S.pos.z.toFixed(0)+' y='+S.pos.y.toFixed(1)+' cur='+M.current;
}
const results=[];
console.log('-- PILOT=1 --');
for(const i of [0,1,2,3]) results.push(runSim('P1 M'+i, 160, i, -1, 1));
for(let p=0;p<PROGS.length;p++) results.push(runSim('P1 '+PROGS[p].name, 180, -1, p, 1));
console.log('-- PILOT=2 (CV) --');
for(const i of [0,1,2,3]) results.push(runSim('P2 M'+i, 160, i, -1, 2));
for(let p=0;p<PROGS.length;p++) results.push(runSim('P2 '+PROGS[p].name, 180, -1, p, 2));
console.log('-- ПОД ВЕТРОМ (wind=1 слабый / 2 шторм) --');
for(const i of [1,3]) results.push(runSim('P1 W1 M'+i, 180, i, -1, 1, 1));
for(const i of [1,3]) results.push(runSim('P1 W2 M'+i, 180, i, -1, 1, 2));
for(const i of [1,3]) results.push(runSim('P2 W1 M'+i, 180, i, -1, 2, 1));
for(const i of [1,3]) results.push(runSim('P2 W2 M'+i, 180, i, -1, 2, 2));
results.forEach(r=>console.log(r));
console.log('-- ASSERT --');
const fails=results.filter(r=>!r.includes('W2') && !r.includes('WIN'));
if(fails.length){ console.error('FAIL:', fails); process.exitCode=1; }
else console.log('OK: '+ results.filter(r=>r.includes('WIN')).length +' wins, W2 storm expected TIMEOUT');
`;

const combined = stub + chunk + tail;
const tmp = path.join(os.tmpdir(), 'drone_trainer_test_' + process.pid + '.js');
fs.writeFileSync(tmp, combined, 'utf8');
try {
  execFileSync(process.execPath, [tmp], { stdio: 'inherit' });
} finally {
  fs.unlinkSync(tmp);
}