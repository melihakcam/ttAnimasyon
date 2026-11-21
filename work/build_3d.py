from pathlib import Path
r=Path(r'D:\tiktokAnimasyon')
(r/'app/halay3d.js').write_text(r'''import * as T from './vendor/three.module.min.js';
const Y=new T.Vector3(0,1,0),v=(x=0,y=0,z=0)=>new T.Vector3(x,y,z);
const geometries=new Map(),materials=new Map();
function geo(key,make){if(!geometries.has(key))geometries.set(key,make());return geometries.get(key)}
function mat(color,roughness=.8,metalness=0){const key=color+':'+roughness+':'+metalness;if(!materials.has(key))materials.set(key,new T.MeshStandardMaterial({color,roughness,metalness}));return materials.get(key)}
const sphere=geo('sphere',()=>new T.SphereGeometry(1,16,12)),cylinder=geo('cylinder',()=>new T.CylinderGeometry(1,1,1,12)),box=geo('box',()=>new T.BoxGeometry(1,1,1));
function mesh(g,m,parent,x,y,z,sx=1,sy=sx,sz=sx){const o=new T.Mesh(g,m);o.position.set(x,y,z);o.scale.set(sx,sy,sz);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o}
function ell(parent,m,x,y,z,sx,sy,sz){return mesh(sphere,m,parent,x,y,z,sx,sy,sz)}
function block(parent,m,x,y,z,sx,sy,sz){return mesh(box,m,parent,x,y,z,sx,sy,sz)}
function bone(parent,m,radius){const o=mesh(cylinder,m,parent,0,0,0,radius,1,radius);o.userData.radius=radius;return o}
function segment(o,a,b){o.position.copy(a).add(b).multiplyScalar(.5);o.scale.y=a.distanceTo(b);o.quaternion.setFromUnitVectors(Y,b.clone().sub(a).normalize())}
function pleatedSkirt(){
 return geo('skirt',()=>{const points=[];for(let i=0;i<8;i++){const q=i/7;points.push(new T.Vector2(.16+q*.18,.94-q*.78))}const g=new T.LatheGeometry(points,48);const pos=g.attributes.position;for(let i=0;i<pos.count;i++){const y=pos.getY(i),a=Math.atan2(pos.getX(i),pos.getZ(i)),fold=1+Math.sin(a*16)*.055*(1-y);pos.setX(i,pos.getX(i)*fold);pos.setZ(i,pos.getZ(i)*fold)}g.computeVertexNormals();return g});
}
function makeActor(user){
 const root=new T.Group(),body=new T.Group();root.add(body);
 const hash=[...user.id].reduce((a,ch)=>a+ch.charCodeAt(0),0),skin=mat(['#c69a77','#d7af8c','#b78564','#e0b99a'][hash%4]),cloth=mat(user.color||'#6d2333'),cream=mat('#d8c49e'),gold=mat('#b79040',.45,.3),dark=mat('#18171a'),hair=mat(['#211814','#3c251b','#171518'][hash%3]);
 const female=user.costume!=='erkek',shirt=mat(female?'#a98661':'#cfb998');
 // Rounded torso and fitted folk waistcoat, with metallic belt and embroidery.
 mesh(geo('torso',()=>new T.CylinderGeometry(.21,.16,.48,20)),shirt,body,0,1.20,0,1,1,.66);
 ell(body,shirt,0,1.42,0,.225,.10,.135);
 if(female){mesh(pleatedSkirt(),cloth,body,0,0,0);mesh(geo('hem',()=>new T.CylinderGeometry(.328,.338,.025,48)),gold,body,0,.185,0);block(body,cloth,-.105,1.25,.104,.14,.39,.045);block(body,cloth,.105,1.25,.104,.14,.39,.045)}
 else {mesh(geo('hips',()=>new T.SphereGeometry(1,16,10)),cloth,body,0,.92,0,.21,.20,.13);block(body,cloth,-.12,1.24,.11,.15,.41,.055);block(body,cloth,.12,1.24,.11,.15,.41,.055)}
 mesh(geo('belt',()=>new T.CylinderGeometry(.181,.184,.065,24)),gold,body,0,.99,0,1,1,.78);
 for(let i=0;i<6;i++){ell(body,gold,-.055,1.08+i*.055,.145,.009,.013,.006);ell(body,gold,.055,1.08+i*.055,.145,.009,.013,.006)}
 // Neck, head and facial detail remain visible beneath the floating profile ring.
 ell(body,skin,0,1.51,0,.064,.085,.061);ell(body,skin,0,1.67,0,.104,.142,.096);
 ell(body,skin,-.105,1.67,0,.025,.042,.02);ell(body,skin,.105,1.67,0,.025,.042,.02);
 ell(body,hair,0,1.74,-.018,.109,.088,.091);
 ell(body,skin,0,1.656,.098,.024,.034,.035);
 for(const x of [-.039,.039]){ell(body,mat('#f1e7d9'),x,1.694,.085,.022,.012,.012);ell(body,dark,x,1.694,.096,.008,.009,.005)}
 ell(body,mat('#8a5547'),0,1.61,.085,.028,.007,.008);
 if(female){
   mesh(geo('cap',()=>new T.SphereGeometry(.115,20,12,0,Math.PI*2,0,Math.PI*.53)),cloth,body,0,1.72,-.006);
   mesh(geo('headband',()=>new T.TorusGeometry(.108,.012,6,32)),gold,body,0,1.741,-.006).rotation.x=Math.PI/2;
   const veil=mesh(geo('veil',()=>new T.CylinderGeometry(.085,.145,.37,18,1,true,0,Math.PI)),cream,body,0,1.54,-.06);veil.rotation.y=Math.PI/2;
   ell(body,gold,-.105,1.615,.01,.014,.026,.012);ell(body,gold,.105,1.615,.01,.014,.026,.012);
 }else{mesh(geo('hat',()=>new T.CylinderGeometry(.111,.113,.09,20)),cloth,body,0,1.805,-.005);mesh(geo('hatband',()=>new T.CylinderGeometry(.115,.115,.019,20)),dark,body,0,1.77,-.005)}
 const legs=[];for(const side of [-1,1]){
  const upper=bone(body,female?skin:cloth,female?.053:.08),lower=bone(body,female?skin:cloth,.052),shoe=ell(body,dark,side*.11,.065,.065,.073,.058,.147);
  legs.push({side,upper,lower,shoe});
 }
 const arms=[];for(const side of [-1,1]){
  const upper=bone(body,cream,.063),lower=bone(body,skin,.047),elbow=ell(body,cream,0,0,0,.064,.064,.064),hand=ell(body,skin,0,0,0,.055,.046,.04);
  arms.push({side,upper,lower,elbow,hand});
 }
 let drum=null;
 if(user.role==='drummer'){
  drum=new T.Group();body.add(drum);drum.position.set(0,.88,.34);drum.rotation.x=Math.PI*.09;
  mesh(geo('drum',()=>new T.CylinderGeometry(.27,.27,.31,32)),cloth,drum,0,0,0);
  for(const h of [-.16,.16])mesh(geo('drumskin',()=>new T.CylinderGeometry(.285,.285,.025,32)),cream,drum,0,h,0);
  for(let a=0;a<Math.PI*2;a+=Math.PI/6){const cord=bone(drum,gold,.008);segment(cord,v(Math.cos(a)*.277,-.15,Math.sin(a)*.277),v(Math.cos(a+.26)*.277,.15,Math.sin(a+.26)*.277))}
 }
 return {root,body,user,legs,arms,drum,phase:hash*.001};
}
function updateLegs(a,time,beat,scale){
 const cycle=time*beat/60*Math.PI*2,step=Math.sin(cycle),lift=Math.max(0,Math.sin(cycle*2))*.035;
 a.body.position.y=lift;
 a.body.rotation.z=Math.sin(cycle)*.025;
 for(const leg of a.legs){const s=leg.side,phase=cycle+(s===1?Math.PI:0);const ankle=v(s*.105+Math.sin(phase)*.04,.09+Math.max(0,Math.sin(phase))*.065,Math.cos(phase)*.065),hip=v(s*.105,.92,0),knee=hip.clone().lerp(ankle,.52);knee.z+=.055+Math.max(0,Math.sin(phase))*.07;segment(leg.upper,hip,knee);segment(leg.lower,knee,ankle);leg.shoe.position.copy(ankle).add(v(0,-.025,.055));leg.shoe.rotation.x=-Math.max(0,Math.sin(phase))*.14}
 a.root.updateMatrixWorld(true);
}
function solveArm(a,arm,target,time,bpm){
 // The target is shared by adjacent dancers: the two wrist endpoints are identical.
 const shoulder=v(arm.side*.205,1.41,0),hand=a.body.worldToLocal(target.clone());
 const mid=shoulder.clone().lerp(hand,.5),distance=shoulder.distanceTo(hand),length=.32;
 const bend=Math.sqrt(Math.max(.001,length*length-distance*distance*.25));
 mid.y-=bend;mid.z+=.045;
 segment(arm.upper,shoulder,mid);segment(arm.lower,mid,hand);arm.elbow.position.copy(mid);arm.hand.position.copy(hand);
}
function floorTexture(){const cn=document.createElement('canvas');cn.width=cn.height=1024;const ctx=cn.getContext('2d');ctx.fillStyle='#715844';ctx.fillRect(0,0,1024,1024);for(let row=0;row<8;row++)for(let col=-1;col<8;col++){let x=col*150+(row%2)*75,y=row*130;ctx.fillStyle=`hsl(28 22% ${33+((row*71+col*13)%9)}%)`;ctx.fillRect(x+2,y+2,146,126);ctx.strokeStyle='#503d30';ctx.strokeRect(x,y,150,130);for(let i=0;i<80;i++){ctx.fillStyle=i%2?'#ffffff08':'#0000000c';ctx.fillRect(x+(i*37)%148,y+(i*53)%127,2,1)}}const tex=new T.CanvasTexture(cn);tex.colorSpace=T.SRGBColorSpace;tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.repeat.set(3,3);return tex}
function rugTexture(){const cn=document.createElement('canvas');cn.width=cn.height=512;const ctx=cn.getContext('2d');ctx.fillStyle='#6d1527';ctx.fillRect(0,0,512,512);for(let i=0;i<12;i++){ctx.strokeStyle=i%2?'#c49b50':'#291c2c';ctx.lineWidth=3;ctx.strokeRect(8+i*3,8+i*3,496-i*6,496-i*6)}for(let x=85;x<500;x+=85)for(let y=85;y<500;y+=85){ctx.fillStyle=(x+y)%2?'#c6a05f':'#e5c78d';ctx.beginPath();ctx.moveTo(x,y-22);ctx.lineTo(x+22,y);ctx.lineTo(x,y+22);ctx.lineTo(x-22,y);ctx.fill();ctx.fillStyle='#1b2232';ctx.fillRect(x-5,y-5,10,10)}const tex=new T.CanvasTexture(cn);tex.colorSpace=T.SRGBColorSpace;return tex}
export function createHalayStage(canvas,{transparent=false}={}){
 const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance',preserveDrawingBuffer:true});
 renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
 const scene=new T.Scene();if(!transparent){scene.background=new T.Color('#13101a');scene.fog=new T.Fog('#13101a',17,35)}
 const camera=new T.PerspectiveCamera(36,540/960,.1,60);camera.position.set(0,7.9,12.7);camera.lookAt(0,.65,-.35);
 scene.add(new T.HemisphereLight('#e4d5be','#4d3029',2));
 const key=new T.DirectionalLight('#ffe1ae',3.1);key.position.set(-3,8,5);key.castShadow=true;key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-7,right:7,top:7,bottom:-7,near:.5,far:24});key.shadow.normalBias=.025;key.shadow.bias=-.0003;scene.add(key);
 const rim=new T.DirectionalLight('#b8c3ee',1.5);rim.position.set(3,4,-6);scene.add(rim);
 const decor=new T.Group();scene.add(decor);decor.visible=!transparent;
 const ground=new T.Mesh(new T.PlaneGeometry(35,35),new T.MeshStandardMaterial({map:floorTexture(),roughness:.98}));ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;decor.add(ground);
 const rugmat=new T.MeshStandardMaterial({map:rugTexture(),roughness:1});
 for(const [x,z,w,h] of [[-1.7,2.9,1.6,1.2],[1.4,3.7,2,1.5]]){const rug=new T.Mesh(new T.PlaneGeometry(w,h),rugmat);rug.rotation.x=-Math.PI/2;rug.position.set(x,.018,z);rug.receiveShadow=true;decor.add(rug)}
 const benchmat=mat('#711c2a');block(decor,benchmat,0,.27,2.1,2.5,.21,.8);block(decor,mat('#c39a51',.45,.2),0,.16,2.1,2.54,.035,.84);for(const x of [-1.05,1.05])for(const z of [1.82,2.38])block(decor,mat('#472f22'),x,.09,z,.07,.2,.07);
 for(let i=0;i<15;i++){const bulb=new T.Mesh(sphere,new T.MeshBasicMaterial({color:'#ffdaa1'}));bulb.scale.setScalar(.025);bulb.position.set((i-7)*.7,3.3+Math.cos(i*.5)*.18,-4);decor.add(bulb)}
 const actors=new Map();let lastSize='',diagnostics={};
 function render(users,time,bpm,mode='halay'){
  const ids=new Set(users.map(u=>u.id));for(const [id,a] of actors){if(!ids.has(id)){scene.remove(a.root);actors.delete(id)}}
  for(const u of users){let a=actors.get(u.id);const signature=u.costume+u.color+u.role;if(!a||a.signature!==signature){if(a)scene.remove(a.root);a=makeActor(u);a.signature=signature;actors.set(u.id,a);scene.add(a.root)}a.user=u}
  const dancers=users.filter(u=>u.role!=='drummer'),n=dancers.length;
  const span=Math.max(.65,Math.min(6.3,(n-1)*.65)),scale=n>1?Math.min(1,span/(n-1)/.65):1;
  const beat=time*bpm/60*Math.PI*2,sideStep=Math.sin(beat)*.065*scale;
  const rows=[];
  for(let i=0;i<n;i++){
   const a=actors.get(dancers[i].id),q=n===1?0:(i/(n-1)*2-1),x=q*span*.5;
   // One open, continuous chain. No opposite partners, no orbiting independent dancers.
   const z=-1.65+1.35*q*q;
   a.root.position.set(x+sideStep,0,z+Math.cos(beat)*.025*scale);a.root.scale.setScalar(scale);a.root.rotation.y=-Math.atan(q*.65)*.55;
   if(mode==='orbit'){a.root.position.z+=Math.sin(time*.35)*.15}
   updateLegs(a,time,bpm,scale);rows.push(a);
  }
  const joins=[];
  for(let i=0;i<rows.length-1;i++){
   const left=rows[i],right=rows[i+1],p=left.root.localToWorld(v(.205,1.17,0)),q=right.root.localToWorld(v(-.205,1.17,0)),target=p.add(q).multiplyScalar(.5);
   target.y+=Math.sin(beat)*.065*scale;joins.push(target);
  }
  let maxGap=0;
  for(let i=0;i<rows.length;i++){
   const a=rows[i];
   for(const arm of a.arms){const neighbor=arm.side===-1?joins[i-1]:joins[i];const target=neighbor||a.root.localToWorld(v(arm.side*.43,1.18+Math.sin(beat)*.08,.06));solveArm(a,arm,target,time,bpm)}
   if(i<rows.length-1){const wrist=a.body.localToWorld(a.arms[1].hand.position.clone()),other=rows[i+1];/* measured again after both arms are solved below */}
  }
  for(let i=0;i<rows.length-1;i++){
   const p=rows[i].body.localToWorld(rows[i].arms[1].hand.position.clone()),q=rows[i+1].body.localToWorld(rows[i+1].arms[0].hand.position.clone());maxGap=Math.max(maxGap,p.distanceTo(q));
  }
  const drummer=users.find(u=>u.role==='drummer');if(drummer){const a=actors.get(drummer.id);a.root.position.set(1.4,.015,3.55);a.root.scale.setScalar(1);a.root.rotation.y=-.22;updateLegs(a,time,bpm,1);for(const arm of a.arms){solveArm(a,arm,a.root.localToWorld(v(arm.side*.18,1.0+Math.sin(beat+arm.side)*.08,.38)),time,bpm)}}
  const w=canvas.clientWidth,h=canvas.clientHeight,size=w+'x'+h;if(size!==lastSize){renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();lastSize=size}
  renderer.render(scene,camera);
  const labels=users.map(u=>{const a=actors.get(u.id),p=a.root.localToWorld(v(0,2.12,0)).project(camera);return {user:u,x:(p.x*.5+.5)*540,y:(-.5*p.y+.5)*960,scale:a.root.scale.x,depth:p.z}}).sort((a,b)=>b.depth-a.depth);
  diagnostics={renderer:'threejs-webgl',chainCount:n,links:Math.max(0,n-1),maxHandGap:maxGap,phase:time,transparent,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles};
  return labels;
 }
 return {render,diagnostics:()=>diagnostics,dispose:()=>renderer.dispose()};
}
''',encoding='utf-8')
# Retain the HUD and user labels on a separate transparent canvas over the 3D scene.
p=r/'app/scene.js';old=p.read_text(encoding='utf-8');(r/'work/scene-before-3d.js').write_text(old,encoding='utf-8')
start=old.index('function hud(');end=old.index('let last=0,phaseTime=0;');hud=old[start:end].replace('Test panelinden demo katılımcıları ekle.','Yorumlarla halaya otomatik katıl.');portrait=old[old.index('const avatars=new Map();'):old.index('function rug(')]
new="""import {connect} from './transport.js';
import {createHalayStage} from './halay3d.js';
const canvas=document.querySelector('#stage'),c=canvas.getContext('2d');
let state={users:[],events:[],bpm:112,scene:'halay'},offset=0;
const transparent=new URLSearchParams(location.search).has('transparent');
let stage;
try{stage=createHalayStage(document.querySelector('#world'),{transparent})}
catch(err){document.querySelector('#connection').textContent='3B sahne açılamadı. Tarayıcıda grafik hızlandırmayı kontrol edin.';throw err}
connect(s=>{state=s;offset=s.server_time-Date.now()/1000;},ok=>{document.querySelector('#connection').textContent=ok?'':'Bağlantı bekleniyor…'});
"""+portrait+hud+"""
let last=0,phaseTime=0;
window.halayDiagnostics=()=>stage.diagnostics();
function frame(ms){
 const dt=Math.min((ms-last)/1000,.05);last=ms;const now=Date.now()/1000+offset;
 phaseTime+=dt*(state.speed_until>now?1.45:1);
 const ratio=Math.min(devicePixelRatio||1,1.5),w=canvas.clientWidth,h=canvas.clientHeight;
 if(canvas.width!==Math.round(w*ratio)||canvas.height!==Math.round(h*ratio)){canvas.width=Math.round(w*ratio);canvas.height=Math.round(h*ratio)}
 c.setTransform(1,0,0,1,0,0);c.clearRect(0,0,canvas.width,canvas.height);
 const s=Math.min(canvas.width/540,canvas.height/960);c.setTransform(s,0,0,s,(canvas.width-540*s)/2,(canvas.height-960*s)/2);
 const users=state.users.filter(u=>u.joined),labels=stage.render(users,phaseTime,state.bpm,state.scene);
 for(const p of labels){
  const u=p.user,r=Math.max(10,19*p.scale),drummer=u.role==='drummer';
  if(drummer)text('🥁 Nağaracı',p.x,p.y-59,16,'#ffe38e');
  portrait(u,p.x,p.y,r);
  const label=u.name.length>15?u.name.slice(0,14)+'…':u.name,width=Math.max(54,label.length*7);
  rounded(p.x-width/2,p.y-r-26,width,21,9,drummer?'#b52542':'#111319d9');text(label,p.x,p.y-r-11,12);
  if(u.bubble&&u.bubble_until>now){const msg=u.bubble.length>22?u.bubble.slice(0,21)+'…':u.bubble;rounded(p.x-84,p.y-r-61,168,27,10,'#fff4e5');text(msg,p.x,p.y-r-43,12,'#30212a')}
 }
 hud(now,users);requestAnimationFrame(frame);
}requestAnimationFrame(frame);
"""
p.write_text(new,encoding='utf-8')
(r/'app/overlay.html').write_text('''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Halay • Yayın sahnesi</title><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:transparent}#viewport{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);height:100%;width:auto;aspect-ratio:9/16;max-width:100%;max-height:100%}@media(min-aspect-ratio:9/16){#viewport{height:100%;width:auto}}@media(max-aspect-ratio:9/16){#viewport{width:100%;height:auto}}canvas{position:absolute;inset:0;width:100%;height:100%;display:block}#stage{pointer-events:none}#connection{position:fixed;bottom:9%;left:5%;color:#fff;background:#9d2136;padding:8px 14px;border-radius:8px;font:15px system-ui}#connection:empty{display:none}</style><div id="viewport"><canvas id="world" aria-label="Üç boyutlu el ele halay sahnesi"></canvas><canvas id="stage" aria-label="İsimler ve yayın göstergeleri"></canvas></div><div id="connection"></div><script type="module" src="/assets/scene.js?v=3"></script></html>''',encoding='utf-8')
print('Connected 3D halay renderer created.')
